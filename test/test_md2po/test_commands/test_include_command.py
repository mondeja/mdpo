import pytest

from mdpo.md2po import markdown_to_pofile


def test_include_comment():
    content = '''<!-- mdpo-include This comment must be included -->
Some text that needs to be clarified

Some text without comment
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "This comment must be included"
msgstr ""

msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''


def test_include_comment_without_value():
    with pytest.raises(ValueError):
        markdown_to_pofile('<!-- mdpo-include -->')


def test_include_comment_with_extracted():
    content = '''<!-- mdpo-translator Comment for translator in comment itself -->
<!-- mdpo-include This comment must be included -->
Some text that needs to be clarified

Some text without comment
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

#. Comment for translator in comment itself
msgid "This comment must be included"
msgstr ""

msgid "Some text that needs to be clarified"
msgstr ""

msgid "Some text without comment"
msgstr ""
'''
