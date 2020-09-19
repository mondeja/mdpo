import pytest

from md2po import markdown_to_pofile


def test_context():
    content = '''<!-- md2po-context month -->
May

<!-- md2po-context might -->
May
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgctxt "month"
msgid "May"
msgstr ""

msgctxt "might"
msgid "May"
msgstr ""
'''


def test_context_without_value():
    with pytest.raises(ValueError):
        markdown_to_pofile('<!-- md2po-context -->')
