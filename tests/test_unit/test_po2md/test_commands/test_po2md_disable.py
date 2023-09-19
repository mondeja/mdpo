import pytest
from mdpo.po2md import Po2Md, pofile_to_markdown


@pytest.mark.parametrize(
    ('commands', 'command_aliases'), (
        ({'disable': 'mdpo-disable', 'enable': 'mdpo-enable'}, {}),
        (
            {'disable': 'mdpo-off', 'enable': 'mdpo-on'},
            {'mdpo-off': 'disable', 'mdpo-on': 'enable'},
        ),
        (
            {'disable': 'off', 'enable': 'on'},
            {'off': 'disable', 'on': 'enable'},
        ),
    ),
)
def test_disable_enable(commands, command_aliases, tmp_file):
    disable_command, enable_command = (commands['disable'], commands['enable'])

    markdown_input = f"""This must be translated.

<!-- {disable_command} -->
This must be ignored.

<!-- {enable_command} -->
This must be translated also.
"""

    markdown_output = """Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.
"""

    pofile_content = """#
msgid ""
msgstr ""

msgid "This must be translated."
msgstr "Esto debe ser traducido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be translated also."
msgstr "Esto también debe ser traducido."
"""

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(
            markdown_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == markdown_output


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-enable-next-line', {}),
        ('on-next-line', {'on-next-line': 'enable-next-line'}),
    ),
)
def test_enable_next_block(command, command_aliases, tmp_file):
    markdown_input = f"""This must be translated.

<!-- mdpo-disable -->

This must be ignored.

<!-- {command} -->
This must be translated also.

This must be ignored also.

<!-- mdpo-enable-next-line -->
# This header must be translated

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be translated.
"""

    markdown_output = """Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.

This must be ignored also.

# Este encabezado debe ser traducido

Other line that must be ignored.

La última línea también debe ser traducida.
"""

    pofile_content = """#
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
"""

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(
            markdown_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == markdown_output


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable-next-block', {}),
        ('mdpo-disable-next-line', {}),
        ('off-next-block', {'off-next-block': 'disable-next-block'}),
        ('off-next-line', {'off-next-line': 'disable-next-line'}),
    ),
)
def test_disable_next_block(command, command_aliases, tmp_file):
    markdown_input = f"""This must be translated.

<!-- {command} -->
This must be ignored.

This must be translated also.
"""

    markdown_output = """Esto debe ser traducido.

This must be ignored.

Esto también debe ser traducido.
"""

    pofile_content = """#
msgid ""
msgstr ""

msgid "This must be translated."
msgstr "Esto debe ser traducido."

msgid "This must be ignored."
msgstr "Esto debe ser ignorado."

msgid "This must be translated also."
msgstr "Esto también debe ser traducido."
"""

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(
            markdown_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == markdown_output


def test_disabled_entries(tmp_file):
    markdown_input = """This must be translated.

<!-- mdpo-disable -->

This must be ignored.

<!-- mdpo-enable-next-block -->
This must be translated also.

This must be ignored also.

<!-- mdpo-enable-next-line -->
# This header must be translated

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be translated.
"""

    pofile_content = """#
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
"""

    with tmp_file(pofile_content, '.po') as po_filepath:
        po2md = Po2Md(po_filepath)
        po2md.translate(markdown_input)

        expected_msgids = [
            'This must be ignored.',
            'This must be ignored also.',
            'Other line that must be ignored.',
        ]

        assert len(po2md.disabled_entries) == len(expected_msgids)

        for expected_msgid in expected_msgids:
            _found_msgid = False
            for entry in po2md.disabled_entries:
                if entry.msgid == expected_msgid:
                    _found_msgid = True

            assert _found_msgid, (
                f"'{expected_msgid}' msgid not found inside disabled_entries"
            )
