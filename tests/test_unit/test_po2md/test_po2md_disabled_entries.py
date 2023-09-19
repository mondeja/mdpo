from mdpo.po2md import Po2Md


def test_disabled_entries(tmp_file):
    po_content = """#
msgid ""
msgstr ""

msgid "foo"
msgstr "translated foo"
"""

    markdown_content = """# foo

<!-- mdpo-translator Message for translator -->
<!-- mdpo-context Context -->
<!-- mdpo-disable-next-line -->
this should be in disabled_entries
"""

    with tmp_file(po_content, '.po') as po_filepath:
        po2md = Po2Md(po_filepath)
        output = po2md.translate(markdown_content)

    assert output == '# translated foo\n\nthis should be in disabled_entries\n'

    assert len(po2md.disabled_entries) == 1

    disabled_entry = po2md.disabled_entries[0]
    assert disabled_entry.msgid == 'this should be in disabled_entries'
    assert disabled_entry.msgstr == ''
    assert disabled_entry.msgctxt == 'Context'
    assert disabled_entry.tcomment == 'Message for translator'
