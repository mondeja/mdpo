import os
import tempfile
from uuid import uuid4

import pytest

from md2po import Md2PoConverter

EMPTY_FILES_DIRNAME = 'empty-files'
EMPTY_FILES_GLOB = os.path.join('test', EMPTY_FILES_DIRNAME, '**', '**.md')


def empty_file_path(directory, filename):
    return os.path.join('test', EMPTY_FILES_DIRNAME, directory, filename)


def test_ignore_files_by_filename():
    md2po_converter = Md2PoConverter(EMPTY_FILES_GLOB,
                                     ignore=['foo04.md', 'bar02.md'])

    assert md2po_converter.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar03.md'),
                                         empty_file_path('foo', 'foo01.md'),
                                         empty_file_path('foo', 'foo02.md'),
                                         empty_file_path('foo', 'foo03.md')]


def test_ignore_directory_by_dirname():
    md2po_converter = Md2PoConverter(EMPTY_FILES_GLOB, ignore=['foo'])

    assert md2po_converter.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar02.md'),
                                         empty_file_path('bar', 'bar03.md')]


def test_ignore_files_by_filepath():
    md2po_converter = Md2PoConverter(
        EMPTY_FILES_GLOB,
        ignore=[os.path.join('test', EMPTY_FILES_DIRNAME, 'foo', 'foo04.md'),
                os.path.join('test', EMPTY_FILES_DIRNAME, 'bar', 'bar02.md')])

    assert md2po_converter.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar03.md'),
                                         empty_file_path('foo', 'foo01.md'),
                                         empty_file_path('foo', 'foo02.md'),
                                         empty_file_path('foo', 'foo03.md')]


def test_ignore_files_by_dirpath():
    md2po_converter = Md2PoConverter(
        EMPTY_FILES_GLOB,
        ignore=[os.path.join('test', EMPTY_FILES_DIRNAME, 'foo')])

    assert md2po_converter.filepaths == [empty_file_path('bar', 'bar01.md'),
                                         empty_file_path('bar', 'bar02.md'),
                                         empty_file_path('bar', 'bar03.md')]


def test_content_converter():
    markdown_content = '''# Header 1

Some awesome text

```fakelanguage
code block
```
'''

    md2po_converter = Md2PoConverter(markdown_content)
    assert md2po_converter.convert().__unicode__() == '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr ""

msgid "Some awesome text"
msgstr ""
'''


def test_init_invalid_content():
    with pytest.raises(ValueError):
        Md2PoConverter('')


def test_mark_not_found_as_absolete():
    tmpdir = tempfile.gettempdir()
    original_md_filepath = os.path.join(tmpdir, uuid4().hex + '.md')
    new_md_filepath = os.path.join(tmpdir, uuid4().hex + '.md')
    po_filepath = os.path.join(tmpdir, uuid4().hex + '.po')

    with open(original_md_filepath, "w") as f:
        f.write('Some string in the markdown\n\nAnother string\n\n')

    with open(new_md_filepath, "w") as f:
        f.write('A new string\n')

    md2po_converter = Md2PoConverter(original_md_filepath)
    pofile = md2po_converter.convert(po_filepath=po_filepath, save=True)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "Some string in the markdown"
msgstr ""

msgid "Another string"
msgstr ""
'''

    md2po_converter = Md2PoConverter(new_md_filepath,
                                     mark_not_found_as_absolete=True)
    pofile = md2po_converter.convert(po_filepath=po_filepath)
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
    md2po_converter = Md2PoConverter(content, msgstr='Default message')
    assert md2po_converter.convert(content).__unicode__() == '''#
msgid ""
msgstr ""

msgid "Mensaje por defecto"
msgstr "Default message"
'''
