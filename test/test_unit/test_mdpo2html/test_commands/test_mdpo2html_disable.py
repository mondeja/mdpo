import pytest

from mdpo.mdpo2html import MdPo2HTML, markdown_pofile_to_html


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable', {}),
        ('off', {'off': 'disable'}),
    ),
)
def test_disable(command, command_aliases, tmp_file):
    html_input = f'''<h1>Header</h1>

<!-- {command} -->

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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = markdown_pofile_to_html(
            html_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == html_output


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

    html_input = f'''<h1>Header</h1>

<!-- {disable_command} -->

<p>This message can not be translated.</p>

<!-- {enable_command} -->
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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = markdown_pofile_to_html(
            html_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == html_output


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-enable-next-line', {}),
        ('on-next-line', {'on-next-line': 'enable-next-line'}),
    ),
)
def test_enable_next_line(command, command_aliases, tmp_file):
    html_input = f'''<h1>Header</h1>

<!-- mdpo-disable -->
<p>This message can not be translated.</p>

<!-- {command} -->
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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = markdown_pofile_to_html(
            html_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == html_output


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable-next-line', {}),
        ('off-next-line', {'off-next-line': 'disable-next-line'}),
    ),
)
def test_disable_next_line(command, command_aliases, tmp_file):
    html_input = f'''<h1>Header</h1>

<!-- {command} -->
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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = markdown_pofile_to_html(
            html_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == html_output


def test_disabled_entries(tmp_file):
    html_input = '''<h1>Header</h1>

<!-- mdpo-disable -->
<p>This message can not be translated.</p>

<!-- mdpo-enable-next-line -->
<p>This message must be translated.</p>

<!-- mdpo-enable -->

<p>This message must be translated also.</p>

<!-- mdpo-disable-next-line -->
<p>This message can not be translated either.</p>
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

msgid "This message can not be translated either."
msgstr "Este mensaje tampoco puede ser traducido."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        mdpo2html = MdPo2HTML(po_filepath)
        mdpo2html.translate(html_input)

        expected_msgids = [
            'This message can not be translated.',
            'This message can not be translated either.',
        ]

        assert len(mdpo2html.disabled_entries) == len(expected_msgids)

        for expected_msgid in expected_msgids:
            _found_msgid = False
            for entry in mdpo2html.disabled_entries:
                if entry.msgid == expected_msgid:
                    _found_msgid = True

            assert _found_msgid, (
                f"'{expected_msgid}' msgid not found inside disabled_entries"
            )
