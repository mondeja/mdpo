import os
import tempfile
from uuid import uuid4

from md2po import (
    Md2PoExtractor,
    FORBIDDEN_CHARS,
    REPLACEMENT_CHARS,
)

FILES_DIRNAME = 'empty-files'
FILES_GLOB = os.path.join('test', FILES_DIRNAME, '**', '**.md')


def test_ignore_files():
    md2po_extractor = Md2PoExtractor(FILES_GLOB,
                                     ignore=['foo04.md', 'bar02.md'])

    assert md2po_extractor.filepaths == [
        'test' + os.sep + FILES_DIRNAME + os.sep + 'bar' + os.sep + 'bar01.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'bar' + os.sep + 'bar03.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'foo' + os.sep + 'foo01.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'foo' + os.sep + 'foo02.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'foo' + os.sep + 'foo03.md',
    ]


def test_ignore_directory():
    md2po_extractor = Md2PoExtractor(FILES_GLOB, ignore=['foo'])

    assert md2po_extractor.filepaths == [
        'test' + os.sep + FILES_DIRNAME + os.sep + 'bar' + os.sep + 'bar01.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'bar' + os.sep + 'bar02.md',
        'test' + os.sep + FILES_DIRNAME + os.sep + 'bar' + os.sep + 'bar03.md',
    ]


def test_forbidden_chars():
    filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.md')

    with open(filepath, 'w') as f:
        f.write(''.join(FORBIDDEN_CHARS) + "\n")

    md2po_extractor = Md2PoExtractor(filepath)

    assert md2po_extractor.extract().__unicode__() == '''#
msgid ""
msgstr ""
'''


def test_replacement_chars():
    filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.md')

    with open(filepath, 'w') as f:
        f.write(''.join(REPLACEMENT_CHARS.keys()) + "\n")

    md2po_extractor = Md2PoExtractor(filepath)

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
                                     mark_not_found_as_absolete=False)
    pofile = md2po_extractor.extract(po_filepath=po_filepath)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid "Some string in the markdown"
msgstr ""

msgid "Another string"
msgstr ""

msgid "A new string"
msgstr ""
'''
