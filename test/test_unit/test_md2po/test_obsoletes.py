"""Test if messages of a PO file are updated when this messages were previously
marked as obsolete.
"""

import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize(
    ('mark_not_found_as_obsolete', 'expected_output'), (
        pytest.param(
            True,
            '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

#~ msgid "Bar"
#~ msgstr ""
''',
            id='mark_not_found_as_obsolete=True',
        ),
        pytest.param(
            False,
            '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr ""

msgid "Foo"
msgstr ""
''',
            id='mark_not_found_as_obsolete=False',
        ),
    ),
)
def test_obsolete_not_equal_found(
    mark_not_found_as_obsolete,
    expected_output,
    tmp_file,
):
    markdown_content = '# Foo'
    pofile_content = '#\nmsgid ""\nmsgstr ""\n\nmsgid "Bar"\nmsgstr ""\n'

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
                mark_not_found_as_obsolete=mark_not_found_as_obsolete,
                location=False,
            ),
        )
    assert output == expected_output


@pytest.mark.parametrize(('default_msgstr'), ('', 'Por defecto'))
def test_obsolete_msgstr_fallback(tmp_file, default_msgstr):
    """If a translated message is marked as obsolete and its msgid is found in
    markdown content, must be directly translated. This behaviour is preferred
    over default msgstr using ``msgstr`` parameter.
    """
    markdown_content = '# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

msgid "Hello"
msgstr "Hola"
'''
        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
                msgstr=default_msgstr,
            ),
        )
    assert output == expected_output


@pytest.mark.parametrize(('default_msgstr'), ('', 'Por defecto'))
def test_fuzzy_obsolete_msgstr_fallback(tmp_file, default_msgstr):
    """If a translated message is marked as obsolete and fuzzy, and his msgid
    is found in markdown content, must be directly translated but needs to be
    marked as fuzzy like the obsolete one. This behaviour is preferred
    over default msgstr using ``msgstr`` parameter.
    """
    markdown_content = '# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#, fuzzy\n'
        '#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

#, fuzzy
msgid "Hello"
msgstr "Hola"
'''

        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
                msgstr=default_msgstr,
            ),
        )
    assert output == expected_output


@pytest.mark.parametrize(('default_msgstr'), ('', 'Por defecto'))
def test_tcomment_obsolete_msgstr_fallback_without_found_tcomment(
    tmp_file,
    default_msgstr,
):
    """If a translated message is marked as obsolete and has a translator
    comment, his msgid is found in markdown content and the found message
    hasn't translator comment, must be directly translated but the tcomment
    of the obsolete one is ignored. This behaviour is preferred over default
    msgstr using ``msgstr`` parameter.
    """
    markdown_content = '# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#. Translator comment\n'
        '#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

msgid "Hello"
msgstr "Hola"
'''

        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
                msgstr=default_msgstr,
            ),
        )
    assert output == expected_output


@pytest.mark.parametrize(('default_msgstr'), ('', 'Por defecto'))
def test_tcomment_obsolete_msgstr_fallback_with_found_tcomment(
    tmp_file,
    default_msgstr,
):
    """If a translated message is marked as obsolete and has a translator
    comment, and his msgid is found in markdown content and the found message
    has a translator comment, must be directly translated and the tcomment
    of the obsolete one is ignored, preserving the translator comment of the
    found message. This behaviour is preferred over default msgstr using
    ``msgstr`` parameter.
    """
    markdown_content = \
        '<!-- mdpo-translator Comment for translator -->\n# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#. Other comment\n'
        '#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

#. Comment for translator
msgid "Hello"
msgstr "Hola"
'''

        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
                msgstr=default_msgstr,
            ),
        )
    assert output == expected_output


def test_obsolete_with_msgctxt_matching_msgstr_fallback(tmp_file):
    """If a translated message with msgctxt is marked as obsolete and his msgid
    with the same msgctxt is found in markdown content, must be directly
    translated.
    """
    markdown_content = '<!-- mdpo-context Context -->\n# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#~ msgctxt "Context"\n'
        '#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

msgctxt "Context"
msgid "Hello"
msgstr "Hola"
'''

        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
            ),
        )
    assert output == expected_output


def test_obsolete_with_msgctxt_not_matching_msgstr_fallback(tmp_file):
    """If a translated message with msgctxt is marked as obsolete and his msgid
    with different msgctxt is found in markdown content, should not be
    translated and the other message (with msgctxt not found) must be marked
    as obsolete (if ``mark_not_found_as_obsolete`` is ``True``).
    """
    markdown_content = '<!-- mdpo-context First context -->\n# Hello'
    pofile_content = (
        '#\nmsgid ""\nmsgstr ""\n\n#~ msgctxt "Second context"\n'
        '#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    )

    with tmp_file(pofile_content, '.po') as po_filepath:
        expected_output = '''#
msgid ""
msgstr ""

msgctxt "First context"
msgid "Hello"
msgstr ""

#~ msgctxt "Second context"
#~ msgid "Hello"
#~ msgstr "Hola"
'''

        output = str(
            markdown_to_pofile(
                markdown_content,
                po_filepath=po_filepath,
            ),
        )
    assert output == expected_output
