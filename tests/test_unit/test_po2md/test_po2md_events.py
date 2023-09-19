"""Tests for po2md events."""

import re

from mdpo.po2md import Po2Md, pofile_to_markdown


def test_link_reference_footnotes(tmp_file):
    def process_footnote_references(self, target, href, title):  # noqa: ARG001
        if re.match(r'^\^\d', target):
            # footnotes are treated as text blocks, so we don't need to
            # translate them here
            return False
        return None

    markdown_content = """# Hello

Here is a [reference link][foo].

This is a footnote[^1]. This is another[^2].

[^1]: This is a footnote content.

[^2]: This is another footnote content.

[foo]: https://github.com/mondeja/mdpo
"""

    pofile_content = """#
msgid ""
msgstr ""

msgid "Hello"
msgstr "Hola"

msgid "Here is a [reference link][foo]."
msgstr "Aquí hay un [link referencia][foo]."

msgid "This is a footnote[^1]. This is another[^2]."
msgstr "Esto es una nota al pie[^1]. Esto es otra[^2]."

msgid "[^1]: This is a footnote content."
msgstr "[^1]: Este es un contenido de nota al pie."

msgid "[^2]: This is another footnote content."
msgstr "[^2]: Este es otro contenido de nota al pie."
"""

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(
            markdown_content,
            po_filepath,
            events={'link_reference': process_footnote_references},
        )

    expected_output = """# Hola

Aquí hay un [link referencia][foo].

Esto es una nota al pie[^1]. Esto es otra[^2].

[^1]: Este es un contenido de nota al pie.

[^2]: Este es otro contenido de nota al pie.

[foo]: https://github.com/mondeja/mdpo
"""

    assert output == expected_output


def test_command_event(tmp_file):
    def _abort_command(self, *args):  # noqa: ARG001
        assert not self.disable
        return False

    input_content = """<!-- mdpo-disable -->
hello

<!-- mdpo-disable -->
hello
"""

    pofile_content = """#
msgid ""
msgstr ""

msgid "hello"
msgstr "hola"
"""
    with tmp_file(pofile_content, '.po') as po_filepath:
        po2md = Po2Md(po_filepath, events={'command': _abort_command})
        output = po2md.translate(input_content)
        assert output == ("""hola

hola
""")


def test_msgid_event(tmp_file):
    def _abort_command(self, *args):  # noqa: ARG001
        return False

    input_content = """hello

hello
"""

    pofile_content = """#
msgid ""
msgstr ""

msgid "hello"
msgstr "hola"
"""
    with tmp_file(pofile_content, '.po') as po_filepath:
        po2md = Po2Md(po_filepath, events={'msgid': _abort_command})
        output = po2md.translate(input_content)
        assert output == '\n'
