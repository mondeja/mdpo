import pytest
from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-include', {}),
        ('this-message-also', {'this-message-also': 'include'}),
    ),
)
def test_include_comment(command, command_aliases):
    content = f'''<!-- {command} This comment must be included -->
Some text that needs to be clarified

Some text without comment
'''
    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
msgid ""
msgstr ""

msgid "This comment must be included"
msgstr ""

msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-include', {}),
        ('this-message-also', {'this-message-also': 'include'}),
    ),
)
def test_include_comment_without_value(command, command_aliases):
    expected_msg = (
        'You need to specify a message for the comment to include with the'
        f" command '{command}'."
    )
    with pytest.raises(ValueError, match=expected_msg):
        markdown_to_pofile(
            f'<!-- {command} -->',
            command_aliases=command_aliases,
        )


def test_include_comment_with_extracted():
    content = '''<!-- mdpo-translator Comment for translator in comment -->
<!-- mdpo-include This comment must be included -->
Some text that needs to be clarified

Some text without comment
'''
    pofile = markdown_to_pofile(content)
    assert pofile == '''#
msgid ""
msgstr ""

#. Comment for translator in comment
msgid "This comment must be included"
msgstr ""

msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''


def test_include_comment_with_extracted_and_context():
    content = '''<!-- mdpo-context Some context for the included -->
<!-- mdpo-translator Comment for translator in comment -->
<!-- mdpo-include This comment must be included -->
Some text that needs to be clarified

Some text without comment
'''
    pofile = markdown_to_pofile(content)
    assert pofile == '''#
msgid ""
msgstr ""

#. Comment for translator in comment
msgctxt "Some context for the included"
msgid "This comment must be included"
msgstr ""

msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''
