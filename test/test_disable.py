from md2po import markdown_to_pofile


def test_disable_next_line():
    content = '''
This must be included.

<!-- md2po-disable-next-line -->
This must be ignored.

This must be included also.
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "This must be included also."
msgstr ""
'''


def test_disable_enable():
    content = '''
This must be included.

<!-- md2po-disable -->
This must be ignored

<!-- md2po-enable -->
This must be included also.
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "This must be included also."
msgstr ""
'''
