from mdpo.po2md import pofile_to_markdown


def test_context(tmp_pofile):
    markdown_input = '''<!-- mdpo-context month -->
May

<!-- mdpo-context might -->
May
'''

    markdown_output = 'Mayo\n\nQuizás\n'

    pofile_content = '''#
msgid ""
msgstr ""

msgctxt "month"
msgid "May"
msgstr "Mayo"

msgctxt "might"
msgid "May"
msgstr "Quizás"
'''

    with tmp_pofile(pofile_content) as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output


def test_context_without_value():
    # not raises Error, is ignored
    assert pofile_to_markdown('<!-- mdpo-context -->', '') == ''
