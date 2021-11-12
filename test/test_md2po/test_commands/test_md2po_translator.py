import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-translator', {}),
        ('hey-translator', {'hey-translator': 'translator'}),
    ),
)
def test_translator_command_paragraph(command, command_aliases):
    content = f'''<!-- {command} This is a comment for a translator -->
Some text that needs to be clarified

Some text without comment
'''

    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
msgid ""
msgstr ""

#. This is a comment for a translator
msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-translator', {}),
        ('hey-translator', {'hey-translator': 'translator'}),
    ),
)
def test_translator_command_without_value(command, command_aliases):
    content = f'''<!-- {command} -->
Some text that needs to be clarified
'''
    expected_msg = (
        'You need to specify a string for the extracted comment with the'
        f' command \'{command}\'.'
    )
    with pytest.raises(ValueError, match=expected_msg):
        markdown_to_pofile(content, command_aliases=command_aliases)
