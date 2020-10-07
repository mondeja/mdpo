import os
import shutil
import tempfile
from uuid import uuid4

import pytest

from mdpo.mdpo2html.__main__ import run
from mdpo.text import striplastline


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


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg, tmp_pofile):
    with tmp_pofile(EXAMPLE['pofile']) as po_filepath:

        output, exitcode = run([EXAMPLE['html-input'],
                                '-p', po_filepath, arg])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg, tmp_pofile):
    with tmp_pofile(EXAMPLE['pofile']) as po_filepath:

        output_html_filepath = os.path.join(
            tempfile.gettempdir(), uuid4().hex + '.html')
        input_html_filepath = os.path.join(
            tempfile.gettempdir(), uuid4().hex + '.html')

        with open(input_html_filepath, "w") as f:
            f.write(EXAMPLE['html-input'])

        output, exitcode = run([input_html_filepath, '-p', po_filepath,
                                arg, output_html_filepath])
        out, err = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']
        assert out == ''

        with open(output_html_filepath, "r") as f:
            output_html_content = f.read()

        assert output_html_content == EXAMPLE['html-output']

        os.remove(input_html_filepath)
        os.remove(output_html_filepath)


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

    input_html_filepath = os.path.join(filesdir, uuid4().hex + '.html')
    with open(input_html_filepath, "w") as f:
        f.write("<p>Included</p>\n\n<p>Excluded</p>\n\n")

    expected_output = "<p>Incluida</p>\n\n<p>Excluded</p>\n\n"

    output, exitcode = run([input_html_filepath, '-p',
                            os.path.join(filesdir, '*.po'),
                            arg, po_filepath_excluded])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert output == expected_output
    assert striplastline(out) == expected_output

    shutil.rmtree(filesdir)
