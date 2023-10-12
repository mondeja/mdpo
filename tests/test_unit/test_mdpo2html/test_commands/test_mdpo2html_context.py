import pytest
from mdpo.mdpo2html import markdown_pofile_to_html


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-context', {}),
        ('contextualization', {'contextualization': 'context'}),
    ),
)
def test_context(command, command_aliases, tmp_file):
    html_input = f'''<!-- {command} month -->
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

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = markdown_pofile_to_html(
            html_input,
            po_filepath,
            command_aliases=command_aliases,
        )
    assert output == html_output


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-context', {}),
        ('contextualization', {'contextualization': 'context'}),
    ),
)
def test_context_without_value(command, command_aliases):
    # does not raises error, is ignored
    assert markdown_pofile_to_html(
        f'<!-- {command} -->',
        '',
        command_aliases=command_aliases,
    ) == f'<!-- {command} -->'
