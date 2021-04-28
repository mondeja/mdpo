from mdpo.md2po import Md2Po, markdown_to_pofile


def test_disable_next_line():
    content = '''
This must be included.

<!-- mdpo-disable-next-line -->
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
    content = '''This must be included.

<!-- mdpo-disable -->
This must be ignored

<!-- mdpo-enable -->
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


def test_disable_enable_raw_inline():
    # enable command is part of the last item in the list
    content = '''This must be included.

<!-- mdpo-disable -->
- `config.development.yml`
- `config.staging.yml`
- `config.production.yml`
<!-- mdpo-enable -->

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


def test_enable_next_line():
    content = '''This must be included.

<!-- mdpo-disable -->

This must be ignored.

<!-- mdpo-enable-next-line -->
This must be included also.

This must be ignored also.

<!-- mdpo-enable-next-line -->
# This header must be included

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be included.
'''

    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "This must be included also."
msgstr ""

msgid "This header must be included"
msgstr ""

msgid "The last line also must be included."
msgstr ""
'''


def test_disabled_entries():
    content = '''This must be included.

<!-- mdpo-disable -->

This must be ignored.

<!-- mdpo-enable-next-line -->
This must be included also.

This must be ignored also.

<!-- mdpo-enable-next-line -->
# This header must be included

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be included.
'''

    md2po = Md2Po(content)
    md2po.extract()

    expected_msgids = [
        'This must be ignored.',
        'This must be ignored also.',
        'Other line that must be ignored.',
    ]

    assert len(md2po.disabled_entries) == len(expected_msgids)

    for expected_msgid in expected_msgids:
        _found_msgid = False
        for entry in md2po.disabled_entries:
            if entry.msgid == expected_msgid:
                _found_msgid = True

        assert _found_msgid, (
            f"'{expected_msgid}' msgid not found inside disabled_entries"
        )
