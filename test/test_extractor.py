import os
import tempfile
from uuid import uuid4

import pytest

from md2po import (
    Md2PoExtractor,
    FORBIDDEN_CHARS,
    REPLACEMENT_CHARS,
)

EMPTY_FILES_DIR = 'empty-files'
EMPTY_FILES_GLOB = os.path.join('test', EMPTY_FILES_DIR, '**', '**.md')


def empty_file_path(directory, filename):
    return 'test' + os.sep + EMPTY_FILES_DIR + \
        os.sep + directory + os.sep + filename


def test_ignore_files():
    md2po_extractor = Md2PoExtractor(EMPTY_FILES_GLOB,
                                     ignore=['foo04.md', 'bar02.md'])

    assert md2po_extractor.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar03.md'),
                                         empty_file_path('foo', 'foo01.md'),
                                         empty_file_path('foo', 'foo02.md'),
                                         empty_file_path('foo', 'foo03.md')]


def test_ignore_directory():
    md2po_extractor = Md2PoExtractor(EMPTY_FILES_GLOB, ignore=['foo'])

    assert md2po_extractor.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar02.md'),
                                         empty_file_path('bar', 'bar03.md')]


def test_content_extractor():
    markdown_content = '''# Header 1

Some awesome text

```fakelanguage
code block
```
'''

    md2po_extractor = Md2PoExtractor(markdown_content)
    assert md2po_extractor.extract().__unicode__() == '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr ""

msgid "Some awesome text"
msgstr ""
'''


def test_init_invalid_content():
    with pytest.raises(ValueError):
        Md2PoExtractor('')


def test_forbidden_chars():
    md2po_extractor = Md2PoExtractor(''.join(FORBIDDEN_CHARS) + "\n")

    assert md2po_extractor.extract().__unicode__() == '''#
msgid ""
msgstr ""
'''


def test_replacement_chars():
    md2po_extractor = Md2PoExtractor(''.join(REPLACEMENT_CHARS.keys()) + "\n")

    assert md2po_extractor.extract().__unicode__() == '''#
msgid ""
msgstr ""

msgid "...'"
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

    md2po_extractor = Md2PoExtractor(original_md_filepath)
    pofile = md2po_extractor.extract(po_filepath=po_filepath, save=True)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "Some string in the markdown"
msgstr ""

msgid "Another string"
msgstr ""
'''

    md2po_extractor = Md2PoExtractor(new_md_filepath,
                                     mark_not_found_as_absolete=True)
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
