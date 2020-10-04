import os
import tempfile
from uuid import uuid4

from mdpo.po2md import pofile_to_markdown


def test_disable_next_line():
    markdown_input = '''This must be included.

<!-- mdpo-disable-next-line -->
This must be ignored.

This must be included also.
'''

    markdown_output = '''Esto debe ser incluido.

Esto también debe ser incluido.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr "Esto debe ser incluido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be included also."
msgstr "Esto también debe ser incluido."
'''

    po_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    with open(po_filepath, "w") as f:
        f.write(pofile_content)

    output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output

    os.remove(po_filepath)


def test_disable_enable():
    markdown_input = '''This must be included.

<!-- mdpo-disable -->
This must be ignored

<!-- mdpo-enable -->
This must be included also.
'''

    markdown_output = '''Esto debe ser incluido.

Esto también debe ser incluido.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr "Esto debe ser incluido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be included also."
msgstr "Esto también debe ser incluido."
'''

    po_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    with open(po_filepath, "w") as f:
        f.write(pofile_content)

    output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output

    os.remove(po_filepath)


def test_enable_next_line():
    markdown_input = '''This must be included.

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

    markdown_output = '''Esto debe ser incluido.

Esto también debe ser incluido.

# Este encabezado debe ser incluido

La última línea también debe ser incluida.
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr "Esto debe ser incluido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be included also."
msgstr "Esto también debe ser incluido."

msgid "This header must be included"
msgstr "Este encabezado debe ser incluido"

msgid "Other line that must be ignored."
msgstr "Otra línea que debe ser ignorada."

msgid "The last line also must be included."
msgstr "La última línea también debe ser incluida."
'''

    po_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    with open(po_filepath, "w") as f:
        f.write(pofile_content)

    output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output

    os.remove(po_filepath)
