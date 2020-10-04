import os
import tempfile
from uuid import uuid4

from mdpo.po2md import pofile_to_markdown


def test_context():
    markdown_input = '''<!-- mdpo-context month -->
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

    po_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    with open(po_filepath, "w") as f:
        f.write(pofile_content)

    output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output

    os.remove(po_filepath)


def test_context_without_value():
    # not raises Error, is ignored
    assert pofile_to_markdown('<!-- mdpo-context -->', '') == ''
