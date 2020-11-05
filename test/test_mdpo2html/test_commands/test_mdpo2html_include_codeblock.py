"""<!-- mdpo-include-codeblock --> command is not supported by mdpo2html
implementation."""

import pytest

from mdpo.mdpo2html import markdown_pofile_to_html


def test_include_codeblock(tmp_file):
    html_input = '''<!-- mdpo-include-codeblock -->'''
    pofile_content = '''#

msgid ""
msgstr ""
'''
    with pytest.warns(SyntaxWarning) as record:
        with tmp_file(pofile_content, ".po") as po_filepath:
            markdown_pofile_to_html(html_input, po_filepath)

    assert len(record) == 1
    assert record[0].message.args[0] == (
        "Code blocks translations is not supported by mdpo2html"
        " implementation."
    )
