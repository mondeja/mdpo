import pytest

from mdpo.md2po import markdown_to_pofile


def test_context():
    content = '''<!-- mdpo-context month -->
May

<!-- mdpo-context might -->
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
        markdown_to_pofile('<!-- mdpo-context -->')
