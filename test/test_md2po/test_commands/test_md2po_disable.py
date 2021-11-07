import pytest

from mdpo.md2po import Md2Po, markdown_to_pofile


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
def test_disable_enable(commands, command_aliases):
    disable_command, enable_command = (commands['disable'], commands['enable'])

    content = f'''This must be included.

<!-- {disable_command} -->
This must be ignored

<!-- {enable_command} -->
This must be included also.
'''
    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
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
    assert pofile == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "This must be included also."
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-enable-next-line', {}),
        ('on-next-line', {'on-next-line': 'enable-next-line'}),
    ),
)
def test_enable_next_line(command, command_aliases):
    content = f'''This must be included.

<!-- mdpo-disable -->

This must be ignored.

<!-- {command} -->
This must be included also.

This must be ignored also.

<!-- {command} -->
# This header must be included

Other line that must be ignored.

<!-- mdpo-enable -->

The last line also must be included.
'''

    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
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


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable-next-line', {}),
        ('off-next-line', {'off-next-line': 'disable-next-line'}),
    ),
)
def test_disable_next_line(command, command_aliases):
    content = f'''<!-- mdpo-disable -->
This must be ignored.

<!-- mdpo-enable -->
This must be included.

<!-- {command} -->
This must be ignored also.

This must be included also.
'''
    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "This must be included also."
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
