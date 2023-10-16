import io
import os

import pytest

from mdpo.mdpo2html.__main__ import run


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
''',
}


def test_stdin(capsys, monkeypatch, tmp_file):
    monkeypatch.setattr('sys.stdin', io.StringIO(EXAMPLE['html-input']))

    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath:
        output, exitcode = run(['-p', po_filepath])
        stdout, stderr = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output'][:-1]  # rstrip("\n")
        assert stdout == EXAMPLE['html-output']
        assert stderr == ''


@pytest.mark.parametrize('arg', ('-q', '--quiet'))
def test_quiet(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath:
        output, exitcode = run([
            EXAMPLE['html-input'],
            '-p', po_filepath, arg,
        ])
        stdout, stderr = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']
        assert stdout == ''
        assert stderr == ''


@pytest.mark.parametrize('arg', ('-s', '--save'))
def test_save(capsys, arg, tmp_file):
    with tmp_file(EXAMPLE['pofile'], '.po') as po_filepath, \
            tmp_file(EXAMPLE['html-input'], '.html') as html_input_filepath, \
            tmp_file(EXAMPLE['html-output'], '.html') as html_output_filepath:

        output, exitcode = run([
            html_input_filepath, '-p', po_filepath,
            arg, html_output_filepath,
        ])
        stdout, _ = capsys.readouterr()

        assert exitcode == 0
        assert output == EXAMPLE['html-output']
        assert stdout == ''

        with open(html_output_filepath, encoding='utf-8') as f:
            output_html_content = f.read()

        assert output_html_content == EXAMPLE['html-output']


@pytest.mark.parametrize('arg', ('-i', '--ignore'))
def test_ignore_files_by_filepath(arg, tmp_dir, capsys):
    expected_output = (
        '<p>Incluida</p>\n\n<p>Excluded</p>\n\n<p>Excluded 2</p>\n\n\n'
    )

    with tmp_dir([
        (
            'included.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Included"\n'
                'msgstr "Incluida"\n\n'
            ),
        ),
        (
            'excluded_1.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Exluded"\n'
                'msgstr "Excluida"\n\n'
            ),
        ),
        (
            'excluded_2.po',
            (
                '#\nmsgid ""\nmsgstr ""\n\nmsgid "Exluded 2"\n'
                'msgstr "Excluida 2"\n\n'
            ),
        ),
        (
            'input.html',
            '<p>Included</p>\n\n<p>Excluded</p>\n\n<p>Excluded 2</p>\n\n',
        ),
    ]) as (
        filesdir, _, excluded_po_1_path, excluded_po_2_path, html_input_path,
    ):
        output, exitcode = run([
            html_input_path,
            '-p',
            os.path.join(filesdir, '*.po'),
            arg,
            excluded_po_1_path,
            arg,
            excluded_po_2_path,
        ])
        stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{output}\n' == expected_output
    assert stdout == expected_output
