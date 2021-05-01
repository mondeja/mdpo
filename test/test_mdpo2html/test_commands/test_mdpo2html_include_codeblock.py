"""<!-- mdpo-include-codeblock --> command is not supported by mdpo2html
implementation."""

import pytest

from mdpo.mdpo2html import markdown_pofile_to_html


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-include-codeblock', {}),
        ('on-codeblock', {'on-codeblock': 'include-codeblock'}),
    ),
)
def test_include_codeblock(command, command_aliases, tmp_file):
    html_input = f'''<!-- {command} -->'''
    pofile_content = '''#

msgid ""
msgstr ""
'''
    with pytest.warns(SyntaxWarning) as record:
        with tmp_file(pofile_content, '.po') as po_filepath:
            markdown_pofile_to_html(
                html_input,
                po_filepath,
                command_aliases=command_aliases,
            )

    assert len(record) == 1
    assert record[0].message.args[0] == (
        'Code blocks translations are not supported by mdpo2html'
        ' implementation.'
    )
