import os
import tempfile
from uuid import uuid4

from mdpo.po2md import pofile_to_markdown


def test_multiple_pofiles_glob():
    pofiles = [
        (
            uuid4().hex + '.po',
            '''#
msgid ""
msgstr ""

msgid "Beyond good intentions, a dictatorship is a dictatorship."
msgstr "Más allá de las buenas intenciones, una dictadura es una dictadura."
''',
        ),
        (
            uuid4().hex + '.po',
            '''#
msgid ""
msgstr ""

msgid "How is it that you think beautiful nerd? Gaaaaaay"
msgstr "¿Cómo es que te parece nerd lo bello? Gaaaaaay"
''',
        ),
    ]

    markdown_content = """
Beyond good intentions, a dictatorship is a dictatorship.

How is it that you think beautiful nerd? Gaaaaaay
"""

    expected_output = """Más allá de las buenas intenciones, una dictadura es una dictadura.

¿Cómo es que te parece nerd lo bello? Gaaaaaay
"""

    with tempfile.TemporaryDirectory() as filesdir:
        for pofile in pofiles:
            with open(os.path.join(filesdir, pofile[0]), 'w') as f:
                f.write(pofile[1])

        pofiles_glob = os.path.join(filesdir, '*.po')

        output = pofile_to_markdown(markdown_content, pofiles_glob)
    assert output == expected_output
