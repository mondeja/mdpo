"""Tests for po2md command line interface."""

import io
import os
import re
import tempfile
from uuid import uuid4

import pytest

from mdpo.po2md.__main__ import run


EXAMPLE = {
    'markdown-input': '# Header 1\n\nSome text here\n',
    'markdown-output': '# Encabezado 1\n\nAlgo de texto aquí\n\n',
    'pofile': '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr "Encabezado 1"

msgid "Some text here"
msgstr "Algo de texto aquí"
''',
}


def test_stdin(capsys, monkeypatch, tmp_file):
    monkeypatch.setattr('sys.stdin', io.StringIO(EXAMPLE['markdown-input']))
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath:
        output, exitcode = run(['-p', po_filepath])
        stdout, _ = capsys.readouterr()

        assert exitcode == 0
        assert f'{output}\n' == EXAMPLE['markdown-output']
        assert stdout == EXAMPLE['markdown-output']


@pytest.mark.parametrize('arg', ('-q', '--quiet'))
def test_quiet(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath:

        output, exitcode = run([
            EXAMPLE['markdown-input'],
            '-p', po_filepath, arg,
        ])
        stdout, stderr = capsys.readouterr()

        assert exitcode == 0
        assert f'{output}\n' == EXAMPLE['markdown-output']
        assert stdout == ''
        assert stderr == ''


@pytest.mark.parametrize('arg', ('-D', '--debug'))
def test_debug(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath, \
            tmp_file(EXAMPLE['markdown-input'], '.md') as input_md_filepath:

        output, exitcode = run([input_md_filepath, '-p', po_filepath, arg])

        assert exitcode == 0
        assert f'{output}\n' == EXAMPLE['markdown-output']

        md_output_checked = False
        stdout, _ = capsys.readouterr()
        outlines = stdout.splitlines()
        for i, line in enumerate(outlines):
            assert re.match(
                (
                    r'^po2md\[DEBUG\]::\d{4,}-\d\d-\d\d\s\d\d:\d\d:\d\d\.\d+::'
                    r'(text|link_reference|msgid|enter_block|command|'
                    r'leave_block|enter_span|leave_span)::'
                ),
                line,
            )
            if line.endswith('leave_block:: DOC'):
                non_debug_lines = '\n'.join([*outlines[i + 1:], ''])
                assert non_debug_lines == EXAMPLE['markdown-output']

                md_output_checked = True
                break

        assert md_output_checked


@pytest.mark.parametrize('arg', ('-s', '--save'))
def test_save(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath, \
            tmp_file(EXAMPLE['markdown-input'], '.md') as input_md_filepath, \
            tmp_file('', '.md') as output_md_filepath:

        output, exitcode = run([
            input_md_filepath, '-p', po_filepath,
            arg, output_md_filepath,
        ])
        stdout, _ = capsys.readouterr()

        assert exitcode == 0
        assert f'{output}\n' == EXAMPLE['markdown-output']
        assert stdout == ''

        with open(output_md_filepath) as f:
            assert f'{f.read()}\n' == EXAMPLE['markdown-output']


@pytest.mark.parametrize('arg', ('-i', '--ignore'))
def test_ignore_files_by_filepath(capsys, arg):
    pofiles = [
        (
            uuid4().hex + '.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Included"\n'
                'msgstr "Incluida"\n\n'
            ),
        ),
        (
            uuid4().hex + '.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Excluded"\n'
                'msgstr "Excluida"\n\n'
            ),
        ),
        (
            uuid4().hex + '.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Excluded 2"\n'
                'msgstr "Excluida 2"\n\n'
            ),
        ),
    ]

    expected_output = 'Incluida\n\nExcluded\n\nExcluded 2\n\n'

    with tempfile.TemporaryDirectory() as filesdir:
        for pofile in pofiles:
            with open(os.path.join(filesdir, pofile[0]), 'w') as f:
                f.write(pofile[1])

        input_md_filepath = os.path.join(filesdir, uuid4().hex + '.md')
        with open(input_md_filepath, 'w') as f:
            f.write('Included\n\nExcluded\n\nExcluded 2\n')

        output, exitcode = run([
            input_md_filepath,
            '-p',
            os.path.join(filesdir, '*.po'),
            arg,
            os.path.join(filesdir, pofiles[1][0]),
            arg,
            os.path.join(filesdir, pofiles[2][0]),
        ])

    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{output}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('-e', '--event'))
def test_events(arg, tmp_file, capsys):
    md_content = '# Foo\n\nBaz\n'
    event_file = '''
def transform_text(self, block, text):
    if text == "Foo":
        self.current_msgid = "Bar"
        return False
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr "Bar es"

msgid "Baz"
msgstr "Baz es"

'''

    expected_output = '# Bar es\n\nBaz es\n\n'
    with tmp_file(event_file, '.py') as py_tmp_filename, \
            tmp_file(pofile_content, '.po') as po_tmp_filename:
        pofile, exitcode = run([
            md_content,
            '-p',
            po_tmp_filename,
            arg,
            f'text: {py_tmp_filename}::transform_text',
        ])
        stdout, _ = capsys.readouterr()

        assert exitcode == 0
        assert f'{pofile}\n' == expected_output
        assert stdout == expected_output
