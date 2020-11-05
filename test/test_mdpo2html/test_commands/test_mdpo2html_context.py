from mdpo.mdpo2html import markdown_pofile_to_html


def test_context(tmp_file):
    html_input = '''<!-- mdpo-context month -->
<p>May</p>

<!-- mdpo-context might -->
<p>May</p>
'''

    html_output = '\n<p>Mayo</p>\n\n<p>Quizás</p>\n'

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

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_pofile_to_html(html_input, po_filepath)
    assert output == html_output


def test_context_without_value():
    # not raises Error, is ignored
    assert markdown_pofile_to_html('<!-- mdpo-context -->', '') == ''
