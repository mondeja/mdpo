import io
import os
import tempfile
from uuid import uuid4

import pytest

from mdpo.po2md.__main__ import run
from mdpo.text import striplastline


if os.environ.get("GITHUB_WORKFLOW"):
    pytest.skip("CLI tests don't work in Github workflows",
                allow_module_level=True)

EXAMPLE = {
    'markdown-input': '# Header 1\n\nSome text here\n',
    'markdown-output': '# Encabezado 1\n\nAlgo de texto aquí\n',
    'pofile': '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr "Encabezado 1"

msgid "Some text here"
msgstr "Algo de texto aquí"
'''
}


def test_stdin(capsys, monkeypatch, tmp_file):
    monkeypatch.setattr('sys.stdin', io.StringIO(EXAMPLE['markdown-input']))
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath:

        output, exitcode = run(['-p', po_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['markdown-output']
        assert striplastline(out) == EXAMPLE['markdown-output']


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath:

        output, exitcode = run([EXAMPLE['markdown-input'],
                                '-p', po_filepath, arg])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['markdown-output']
        assert out == ''


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath, \
            tmp_file(EXAMPLE['markdown-input'], ".md") as input_md_filepath, \
            tmp_file("", ".md") as output_md_filepath:

        output, exitcode = run([input_md_filepath, '-p', po_filepath,
                                arg, output_md_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['markdown-output']
        assert out == ''

        with open(output_md_filepath, "r") as f:
            output_markdown_content = f.read()

        assert output_markdown_content == EXAMPLE['markdown-output']


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg):
    pofiles = [
        (
            uuid4().hex + '.po',
            ('#\nmsgid ""\nmsgstr ""\n\nmsgid "Included"\n'
             'msgstr "Incluida"\n\n'),
        ),
        (
            uuid4().hex + '.po',
            ('#\nmsgid ""\nmsgstr ""\n\nmsgid "Exluded"\n'
             'msgstr "Excluida"\n\n'),
        )
    ]

    expected_output = "Incluida\n\nExcluded\n"

    with tempfile.TemporaryDirectory() as filesdir:
        for pofile in pofiles:
            with open(os.path.join(filesdir, pofile[0]), "w") as f:
                f.write(pofile[1])

        input_md_filepath = os.path.join(filesdir, uuid4().hex + '.md')
        with open(input_md_filepath, "w") as f:
            f.write("Included\n\nExcluded\n\n")

        output, exitcode = run([input_md_filepath, '-p',
                                os.path.join(filesdir, '*.po'),
                                arg, os.path.join(filesdir, pofiles[1][0])])
        out, err = capsys.readouterr()

    assert exitcode == 0
    assert output == expected_output
    assert striplastline(out) == expected_output
