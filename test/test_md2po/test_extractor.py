import os
import tempfile
from uuid import uuid4

from mdpo.md2po import Md2Po


def test_content_extractor():
    markdown_content = '''# Header 1

Some awesome text

```fakelanguage
code block
```
'''

    md2po_extractor = Md2Po(markdown_content)
    assert md2po_extractor.extract().__unicode__() == '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr ""

msgid "Some awesome text"
msgstr ""
'''


def test_mark_not_found_as_absolete():
    tmpdir = tempfile.gettempdir()
    original_md_filepath = os.path.join(tmpdir, uuid4().hex + '.md')
    new_md_filepath = os.path.join(tmpdir, uuid4().hex + '.md')
    po_filepath = os.path.join(tmpdir, uuid4().hex + '.po')

    with open(original_md_filepath, "w") as f:
        f.write('Some string in the markdown\n\nAnother string\n\n')

    with open(new_md_filepath, "w") as f:
        f.write('A new string\n')

    md2po_extractor = Md2Po(original_md_filepath)
    pofile = md2po_extractor.extract(po_filepath=po_filepath, save=True)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "Some string in the markdown"
msgstr ""

msgid "Another string"
msgstr ""
'''

    md2po_extractor = Md2Po(new_md_filepath, mark_not_found_as_absolete=True)
    pofile = md2po_extractor.extract(po_filepath=po_filepath)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "A new string"
msgstr ""

#~ msgid "Some string in the markdown"
#~ msgstr ""

#~ msgid "Another string"
#~ msgstr ""
'''


def test_msgstr():
    content = 'Mensaje por defecto'
    md2po_extractor = Md2Po(content, msgstr='Default message')
    assert md2po_extractor.extract(content).__unicode__() == '''#
msgid ""
msgstr ""

msgid "Mensaje por defecto"
msgstr "Default message"
'''
