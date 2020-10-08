import os
import shutil
import tempfile
from uuid import uuid4

import pytest

from mdpo.po2md.__main__ import run
from mdpo.text import striplastline


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


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg, tmp_pofile):
    with tmp_pofile(EXAMPLE['pofile']) as po_filepath:

        output, exitcode = run([EXAMPLE['markdown-input'],
                                '-p', po_filepath, arg])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['markdown-output']
        assert out == ''


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg, tmp_pofile):
    with tmp_pofile(EXAMPLE['pofile']) as po_filepath:

        output_markdown_filepath = os.path.join(
            tempfile.gettempdir(), uuid4().hex + '.md')
        input_markdown_filepath = os.path.join(
            tempfile.gettempdir(), uuid4().hex + '.md')

        with open(input_markdown_filepath, "w") as f:
            f.write(EXAMPLE['markdown-input'])

        output, exitcode = run([input_markdown_filepath, '-p', po_filepath,
                                arg, output_markdown_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['markdown-output']
        assert out == ''

        with open(output_markdown_filepath, "r") as f:
            output_markdown_content = f.read()

        assert output_markdown_content == EXAMPLE['markdown-output']

        os.remove(input_markdown_filepath)
        os.remove(output_markdown_filepath)


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg):
    filesdir = os.path.join(tempfile.gettempdir(), uuid4().hex)
    os.mkdir(filesdir)

    po_filepath_included = os.path.join(filesdir, uuid4().hex + '.po')
    po_included_content = (
        '#\n\nmsgid ""\nmsgstr ""\n\nmsgid "Included"\nmsgstr "Incluida"\n\n'
    )

    po_filepath_excluded = os.path.join(filesdir, uuid4().hex + '.po')
    po_excluded_content = (
        '#\n\nmsgid ""\nmsgstr ""\n\nmsgid "Exluded"\nmsgstr "Excluida"\n\n'
    )

    with open(po_filepath_included, "w") as f:
        f.write(po_included_content)
    with open(po_filepath_excluded, "w") as f:
        f.write(po_excluded_content)

    input_markdown_filepath = os.path.join(filesdir, uuid4().hex + '.md')
    with open(input_markdown_filepath, "w") as f:
        f.write("Included\n\nExcluded\n\n")

    expected_output = "Incluida\n\nExcluded\n"

    output, exitcode = run([input_markdown_filepath, '-p',
                            os.path.join(filesdir, '*.po'),
                            arg, po_filepath_excluded])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert output == expected_output
    assert striplastline(out) == expected_output

    shutil.rmtree(filesdir)
