from mdpo.mdpo2html import markdown_pofile_to_html


def test_disable(tmp_pofile):
    html_input = '''<h1>Header</h1>

<!-- mdpo-disable -->

<p>This message can not be translated.</p>
'''

    html_output = '''<h1>Encabezado</h1>


<p>This message can not be translated.</p>
'''

    pofile_content = '''#

msgid ""
msgstr ""

msgid "Header"
msgstr "Encabezado"

msgid "This message can not be translated."
msgstr "Este mensaje no puede ser traducido."
'''

    with tmp_pofile(pofile_content) as po_filepath:
        output = markdown_pofile_to_html(html_input, po_filepath)
    assert output == html_output


def test_disable_enable(tmp_pofile):
    html_input = '''<h1>Header</h1>

<!-- mdpo-disable -->

<p>This message can not be translated.</p>

<!-- mdpo-enable -->
<p>This message must be translated.</p>
'''

    html_output = '''<h1>Encabezado</h1>


<p>This message can not be translated.</p>

<p>Este mensaje debe ser traducido.</p>
'''

    pofile_content = '''#

msgid ""
msgstr ""

msgid "Header"
msgstr "Encabezado"

msgid "This message can not be translated."
msgstr "Este mensaje no puede ser traducido."

msgid "This message must be translated."
msgstr "Este mensaje debe ser traducido."
'''

    with tmp_pofile(pofile_content) as po_filepath:
        output = markdown_pofile_to_html(html_input, po_filepath)
    assert output == html_output


def test_disable_next_line(tmp_pofile):
    html_input = '''<h1>Header</h1>

<!-- mdpo-disable-next-line -->
<p>This message can not be translated.</p>

<p>This message must be translated.</p>
'''

    html_output = '''<h1>Encabezado</h1>

<p>This message can not be translated.</p>

<p>Este mensaje debe ser traducido.</p>
'''

    pofile_content = '''#

msgid ""
msgstr ""

msgid "Header"
msgstr "Encabezado"

msgid "This message can not be translated."
msgstr "Este mensaje no puede ser traducido."

msgid "This message must be translated."
msgstr "Este mensaje debe ser traducido."
'''

    with tmp_pofile(pofile_content) as po_filepath:
        output = markdown_pofile_to_html(html_input, po_filepath)
    assert output == html_output


def test_enable_next_line(tmp_pofile):
    html_input = '''<h1>Header</h1>

<!-- mdpo-disable -->
<p>This message can not be translated.</p>

<!-- mdpo-enable-next-line -->
<p>This message must be translated.</p>

<!-- mdpo-enable -->

<p>This message must be translated also.</p>
'''

    html_output = '''<h1>Encabezado</h1>

<p>This message can not be translated.</p>

<p>Este mensaje debe ser traducido.</p>


<p>Este mensaje también debe ser traducido.</p>
'''

    pofile_content = '''#

msgid ""
msgstr ""

msgid "Header"
msgstr "Encabezado"

msgid "This message can not be translated."
msgstr "Este mensaje no puede ser traducido."

msgid "This message must be translated."
msgstr "Este mensaje debe ser traducido."

msgid "This message must be translated also."
msgstr "Este mensaje también debe ser traducido."
'''

    with tmp_pofile(pofile_content) as po_filepath:
        output = markdown_pofile_to_html(html_input, po_filepath)
    assert output == html_output
