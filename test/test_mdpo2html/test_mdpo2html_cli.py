import io
import os
import tempfile
from uuid import uuid4

import pytest

from mdpo.mdpo2html.__main__ import run
from mdpo.text import striplastline


if os.environ.get("GITHUB_WORKFLOW"):
    pytest.skip("CLI tests don't work in Github workflows",
                allow_module_level=True)

EXAMPLE = {
    'html-input': '<h1>Header 1</h1>\n\n<p>Some text here</p>\n',
    'html-output': '<h1>Encabezado 1</h1>\n\n<p>Algo de texto aquí</p>\n',
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
    monkeypatch.setattr('sys.stdin', io.StringIO(EXAMPLE['html-input']))
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath:

        output, exitcode = run(['-p', po_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output'][:-1]  # rstrip("\n")
        assert out == EXAMPLE['html-output']


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath:

        output, exitcode = run([EXAMPLE['html-input'],
                                '-p', po_filepath, arg])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], ".po") as po_filepath, \
            tmp_file(EXAMPLE['html-input'], ".html") as html_input_filepath, \
            tmp_file(EXAMPLE['html-output'], ".html") as html_output_filepath:

        output, exitcode = run([html_input_filepath, '-p', po_filepath,
                                arg, html_output_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']
        assert out == ''

        with open(html_output_filepath, "r") as f:
            output_html_content = f.read()

        assert output_html_content == EXAMPLE['html-output']


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg, tmp_file):
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

    html_input = "<p>Included</p>\n\n<p>Excluded</p>\n\n"
    expected_output = "<p>Incluida</p>\n\n<p>Excluded</p>\n\n"

    with tempfile.TemporaryDirectory() as filesdir:
        for pofile in pofiles:
            with open(os.path.join(filesdir, pofile[0]), "w") as f:
                f.write(pofile[1])
        with tmp_file(html_input, ".html") as html_input_filepath:
            output, exitcode = run([html_input_filepath, '-p',
                                    os.path.join(filesdir, '*.po'),
                                    arg, pofiles[1][0]])
            out, err = capsys.readouterr()

    assert exitcode == 0
    assert output == expected_output
    assert striplastline(out) == expected_output
