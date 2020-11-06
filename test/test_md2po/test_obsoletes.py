"""Test if messages of a pofile are updated when this messages were previously
marked as obsolete."""

import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize('mark_not_found_as_absolete', (True, False))
def test_obsolete_equal_found(tmp_file, mark_not_found_as_absolete):
    markdown_content = '# Foo'
    pofile_content = \
        '#\nmsgid ""\nmsgstr ""\n\n#~ msgid "Foo"\n#~ msgstr ""\n'
    expected_output = '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n'

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath,
            mark_not_found_as_absolete=mark_not_found_as_absolete
        ).__unicode__()
    assert output == expected_output


@pytest.mark.parametrize(('mark_not_found_as_absolete', 'expected_output'), (
    (
        True,
        '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

#~ msgid "Bar"
#~ msgstr ""
'''
    ),
    (
        False,
        '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr ""

msgid "Foo"
msgstr ""
'''
    )
))
def test_obsolete_not_equal_found(mark_not_found_as_absolete, expected_output,
                                  tmp_file):
    markdown_content = '# Foo'
    pofile_content = '#\nmsgid ""\nmsgstr ""\n\nmsgid "Bar"\nmsgstr ""\n'

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath,
            mark_not_found_as_absolete=mark_not_found_as_absolete
        ).__unicode__()
    assert output == expected_output


@pytest.mark.parametrize(("default_msgstr"), ("", "Por defecto"))
def test_obsolete_msgstr_fallback(tmp_file, default_msgstr):
    """If a translated message is marked as obsolete and his msgid is found in
    markdown content, must be directly translated. This behaviour is preferred
    over default msgstr using ``msgstr`` parameter.
    """
    markdown_content = '# Hello'
    pofile_content = \
        '#\nmsgid ""\nmsgstr ""\n\n#~ msgid "Hello"\n#~ msgstr "Hola"\n'
    expected_output = '''#
msgid ""
msgstr ""

msgid "Hello"
msgstr "Hola"
'''

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath, msgstr=default_msgstr,
        ).__unicode__()
    assert output == expected_output


def test_obsolete_with_msgctxt_matching_msgstr_fallback(tmp_file):
    """If a translated message with msgctxt is marked as obsolete and his msgid
    with the same msgctxt is found in markdown content, must be directly
    translated.
    """
    markdown_content = '<!-- mdpo-context Context -->\n# Hello'
    pofile_content = ('#\nmsgid ""\nmsgstr ""\n\n#~ msgctxt "Context"\n'
                      '#~ msgid "Hello"\n#~ msgstr "Hola"\n')
    expected_output = '''#
msgid ""
msgstr ""

msgctxt "Context"
msgid "Hello"
msgstr "Hola"
'''

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath,
        ).__unicode__()
    assert output == expected_output


def test_obsolete_with_msgctxt_not_matching_msgstr_fallback(tmp_file):
    """If a translated message with msgctxt is marked as obsolete and his msgid
    with different msgctxt is found in markdown content, should not be
    translated and the other message (with msgctxt not found) must be marked
    as obsolete (if ``mark_not_found_as_absolete`` is ``True``).
    """
    markdown_content = '<!-- mdpo-context First context -->\n# Hello'
    pofile_content = ('#\nmsgid ""\nmsgstr ""\n\n#~ msgctxt "Second context"\n'
                      '#~ msgid "Hello"\n#~ msgstr "Hola"\n')
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

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath,
        ).__unicode__()
    assert output == expected_output
