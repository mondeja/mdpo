import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-context', {}),
        ('contextualization', {'contextualization': 'context'}),
    ),
)
def test_context(command, command_aliases):
    content = f'''<!-- mdpo-context month -->
May

<!-- {command} might -->
May
'''
    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
    assert pofile == '''#
msgid ""
msgstr ""

msgctxt "month"
msgid "May"
msgstr ""

msgctxt "might"
msgid "May"
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-context', {}),
        ('contextualization', {'contextualization': 'context'}),
    ),
)
def test_context_without_value(command, command_aliases):
    expected_msg = (
        'You need to specify a string for the context with the command'
        f' \'{command}\'.'
    )
    with pytest.raises(ValueError, match=expected_msg):
        markdown_to_pofile(
            f'<!-- {command} -->',
            command_aliases=command_aliases,
        )
