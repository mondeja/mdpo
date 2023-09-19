from mdpo.po2md import Po2Md


def test_translated_entries(tmp_file):
    po_content = """#
msgid ""
msgstr ""

msgctxt "Context"
msgid "foo"
msgstr "translated foo"
"""

    markdown_content = """<!-- mdpo-translator Message for translator -->
<!-- mdpo-context Context -->
# foo

<!-- mdpo-disable-next-line -->
this should be in disabled_entries
"""

    with tmp_file(po_content, '.po') as po_filepath:
        po2md = Po2Md(po_filepath)
        output = po2md.translate(markdown_content)

    assert output == '# translated foo\n\nthis should be in disabled_entries\n'

    assert len(po2md.translated_entries) == 1

    translated_entry = po2md.translated_entries[0]
    assert translated_entry.msgid == 'foo'
    assert translated_entry.msgstr == 'translated foo'
    assert translated_entry.msgctxt == 'Context'
    assert translated_entry.tcomment == 'Message for translator'
