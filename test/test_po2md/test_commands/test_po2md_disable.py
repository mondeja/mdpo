from mdpo.po2md import pofile_to_markdown


def test_disable_next_line(tmp_file):
    markdown_input = '''This must be translated.

<!-- mdpo-disable-next-line -->
This must be ignored.

This must be translated also.
'''

    markdown_output = '''Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be translated."
msgstr "Esto debe ser traducido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be translated also."
msgstr "Esto también debe ser traducido."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output


def test_disable_enable(tmp_file):
    markdown_input = '''This must be translated.

<!-- mdpo-disable -->
This must be ignored.

<!-- mdpo-enable -->
This must be translated also.
'''

    markdown_output = '''Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be translated."
msgstr "Esto debe ser traducido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be translated also."
msgstr "Esto también debe ser traducido."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output


def test_enable_next_line(tmp_file):
    markdown_input = '''This must be translated.

<!-- mdpo-disable -->

This must be ignored.

<!-- mdpo-enable-next-line -->
This must be translated also.

This must be ignored also.

<!-- mdpo-enable-next-line -->
# This header must be translated

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be translated.
'''

    markdown_output = '''Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.

This must be ignored also.

# Este encabezado debe ser traducido

Other line that must be ignored.

La última línea también debe ser traducida.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be translated."
msgstr "Esto debe ser traducido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be translated also."
msgstr "Esto también debe ser traducido."

msgid "This header must be translated"
msgstr "Este encabezado debe ser traducido"

msgid "Other line that must be ignored."
msgstr "Otra línea que debe ser ignorada."

msgid "The last line also must be translated."
msgstr "La última línea también debe ser traducida."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output
