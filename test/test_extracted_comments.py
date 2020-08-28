import pytest

from md2po import markdown_to_pofile


def test_translator_command_paragraph():
    content = '''<!-- md2po-translator This is a comment for a translator -->
Some text that needs to be clarified

Some text without comment
'''

    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

#. This is a comment for a translator
msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''


def test_translator_command_no_value():
    content = '''<!-- md2po-translator -->
Some text that needs to be clarified
'''

    with pytest.raises(ValueError):
        markdown_to_pofile(content)
