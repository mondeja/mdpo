"""Test if messages of a pofile are updated when this messages were previously
marked as obsolete."""

import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize('mark_not_found_as_absolete', (True, False))
def test_obsolete_equal_found(tmp_file, mark_not_found_as_absolete):
    markdown_content = '# Foo'
    pofile_content = \
        '#\n\nmsgid ""\nmsgstr ""\n\n#~ msgid "Foo"\n#~ msgstr ""\n'
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
    pofile_content = '#\n\nmsgid ""\nmsgstr ""\n\nmsgid "Bar"\nmsgstr ""\n'

    with tmp_file(pofile_content, ".po") as po_filepath:
        output = markdown_to_pofile(
            markdown_content, po_filepath=po_filepath,
            mark_not_found_as_absolete=mark_not_found_as_absolete
        ).__unicode__()
    assert output == expected_output
