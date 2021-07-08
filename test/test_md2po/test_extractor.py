import tempfile

import pytest

from mdpo.md2po import Md2Po


def test_content_extractor():
    markdown_content = '''# Header 1

Some awesome text

```fakelanguage
code block
```
'''

    md2po = Md2Po(markdown_content)
    assert md2po.extract().__unicode__() == '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr ""

msgid "Some awesome text"
msgstr ""
'''


def test_mark_not_found_as_obsolete(tmp_file):
    original_md_file_content = (
        'Some string in the markdown\n\n'
        'Another string\n\n'
    )
    new_md_file_content = 'A new string\n'
    po_file = tempfile.NamedTemporaryFile(suffix='.po')

    with tmp_file(original_md_file_content, '.md') as original_md_filepath:
        md2po = Md2Po(original_md_filepath)
        po = md2po.extract(po_filepath=po_file.name, save=True)
    assert po.__unicode__() == f'''#
msgid ""
msgstr ""

#: {original_md_filepath}:block 1 (paragraph)
msgid "Some string in the markdown"
msgstr ""

#: {original_md_filepath}:block 2 (paragraph)
msgid "Another string"
msgstr ""
'''

    with tmp_file(new_md_file_content, '.md') as new_md_filepath:
        md2po = Md2Po(
            new_md_filepath,
            mark_not_found_as_obsolete=True,
        )
        po = md2po.extract(po_filepath=po_file.name)
    assert po.__unicode__() == f'''#
msgid ""
msgstr ""

#: {new_md_filepath}:block 1 (paragraph)
msgid "A new string"
msgstr ""

#~ msgid "Some string in the markdown"
#~ msgstr ""

#~ msgid "Another string"
#~ msgstr ""
'''

    po_file.close()


def test_msgstr():
    content = 'Mensaje por defecto'
    md2po = Md2Po(content, msgstr='Default message')
    assert md2po.extract(content).__unicode__() == '''#
msgid ""
msgstr ""

msgid "Mensaje por defecto"
msgstr "Default message"
'''


def test_ignore_msgids():
    content = 'foo\n\nbar\n\nbaz\n'
    md2po = Md2Po(content, ignore_msgids=['foo', 'baz'])
    assert md2po.extract(content).__unicode__() == '''#
msgid ""
msgstr ""

msgid "bar"
msgstr ""
'''


def test_md2po_save_without_po_filepath():
    content = 'foo\n\nbar\n\nbaz\n'
    md2po = Md2Po(content)
    with pytest.raises(ValueError) as exc:
        md2po.extract(save=True)

    assert str(exc.value) == (
        "The argument 'save' does not make sense without passing the"
        " argument 'po_filepath'."
    )
