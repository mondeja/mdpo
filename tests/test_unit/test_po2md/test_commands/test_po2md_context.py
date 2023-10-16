import pytest

from mdpo.po2md import pofile_to_markdown


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-context', {}),
        ('contextualization', {'contextualization': 'context'}),
    ),
)
def test_context(command, command_aliases, tmp_file):
    markdown_input = f'''<!-- {command} month -->
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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(
            markdown_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == markdown_output


@pytest.mark.parametrize('command', ('mdpo-context', 'contextualization'))
def test_context_without_value(command):
    # does not raises error, is ignored
    assert pofile_to_markdown(f'<!-- {command} -->', '') == ''
