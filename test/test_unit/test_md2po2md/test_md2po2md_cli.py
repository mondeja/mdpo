"""Tests for ``md2po2md`` CLI"""

import os
import shutil
import tempfile
from uuid import uuid4

import pytest

from mdpo.md2po2md.__main__ import run


@pytest.mark.parametrize('output_arg', ('-o', '--output'))
@pytest.mark.parametrize('langs_arg', ('-l', '--lang'))
@pytest.mark.parametrize('all_langs_in_same_arg', (True, False))
@pytest.mark.parametrize(
    (
        'langs',
        'input_paths_glob',
        'output',
        'input_files_content',
        'expected_files_content',
    ),
    (
        pytest.param(
            ['es'],
            'README.md',
            'locale/{lang}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'locale/es/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/es/README.md': 'Foo\n\nBar\n',
            },
            id='es-locale/{lang}',
        ),
        pytest.param(
            ('es', 'fr'),
            'README.md',
            'locale/{lang}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'locale/es/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/es/README.md': 'Foo\n\nBar\n',
                'locale/fr/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/fr/README.md': 'Foo\n\nBar\n',
            },
            id='README-es,fr-locale/{lang}',
        ),
        pytest.param(
            ('es',),
            'README.md',
            'locale/',
            {},
            ValueError,
            id='es-locale/-ValueError',
        ),
        pytest.param(
            ('es',),
            'README.md',
            'locale/{lang}/{basename}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'locale/es/README.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/es/README': 'Foo\n\nBar\n',
            },
            id='es-locale/{lang}/{basename}',
        ),
        pytest.param(
            ['es'],
            'README.md',
            '{lang}/{basename}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'es/README.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'es/README': 'Foo\n\nBar\n',
            },
            id='es-{lang}/{basename}',
        ),
        pytest.param(
            ['es'],
            'README.md',
            '{lang}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'es/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'es/README.md': 'Foo\n\nBar\n',
            },
            id='es-{lang}',
        ),
        pytest.param(
            ['es'],
            '[s-m]',
            '{lang}/{basename}',
            {},
            ValueError,
            id='invalid-glob-ValueError',
        ),
        pytest.param(
            ['es'],
            'foobar*',
            '{lang}/{basename}',
            {},
            FileNotFoundError,
            id='no-files-matching-input-glob',
        ),
        pytest.param(
            ('es', 'fr', 'de_DE'),
            'README.md',
            'locale/{lang}',
            {'README.md': 'Foo\n\nBar\n'},
            {
                'locale/es/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/es/README.md': 'Foo\n\nBar\n',
                'locale/fr/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/fr/README.md': 'Foo\n\nBar\n',
                'locale/de_DE/README.md.po': (
                    '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n\n'
                    'msgid "Bar"\nmsgstr ""\n'
                ),
                'locale/de_DE/README.md': 'Foo\n\nBar\n',
            },
            id='README-es,fr-locale/{lang}',
        ),
    ),
)
def test_md2po2md_arguments(
    output_arg,
    langs_arg,
    all_langs_in_same_arg,
    langs,
    input_paths_glob,
    output,
    input_files_content,
    expected_files_content,
):
    # create base directory and files
    basedir = os.path.join(tempfile.gettempdir(), uuid4().hex[:8])
    if os.path.isdir(basedir):
        shutil.rmtree(basedir)
    os.mkdir(basedir)

    for relpath, content in input_files_content.items():
        filepath = os.path.join(basedir, relpath)
        with open(filepath, 'w') as f:
            f.write(content)

    def cleanup():
        if os.path.isdir(basedir):
            shutil.rmtree(basedir)

    # run md2po2md
    cmd = [
        os.path.join(basedir, input_paths_glob),
        output_arg, os.path.join(basedir, output),
    ]

    # if all languages are passed in the same `--lang`/`-l` argument
    if all_langs_in_same_arg:
        cmd.extend([langs_arg, *langs])
    else:
        for lang in langs:
            cmd.extend([langs_arg, lang])

    cmd.append('--no-location')

    if hasattr(expected_files_content, '__traceback__'):
        with pytest.raises(expected_files_content):
            run(cmd)
        return cleanup()
    run(cmd)

    # Check number of files
    expected_number_of_files = (
        len(expected_files_content.keys()) + len(input_files_content.keys())
    )
    n_files = 0
    for root, dirs, files in os.walk(basedir, topdown=False):
        n_files += len(files)
    assert n_files == expected_number_of_files

    # Check expected content
    for relpath, content in expected_files_content.items():
        filepath = os.path.join(basedir, relpath)
        with open(filepath) as f:
            assert f.read() == content

    cleanup()
