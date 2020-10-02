import os
import shutil
import tempfile
from uuid import uuid4

import pytest

from mdpo.md2po.__main__ import run
from mdpo.text import striplastline


EXAMPLE = {
    'input': '# Header 1\n\nSome text here',
    'output': '''#
msgid ""
msgstr ""

msgid "Header 1"
msgstr ""

msgid "Some text here"
msgstr ""
'''
}


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg):
    pofile, exitcode = run([EXAMPLE['input'], arg])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert pofile.__unicode__() == EXAMPLE['output']
    assert out == ''


@pytest.mark.parametrize('arg', ['-po', '--po-filepath'])
def test_po_filepath(capsys, arg):
    pofile_path = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    pofile_content = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''

    with open(pofile_path, 'w') as f:
        f.write(pofile_content)

    markdown_content = '# Bar\n'

    pofile, exitcode = run([markdown_content, arg, pofile_path])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Bar"
msgstr ""
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output

    os.remove(pofile_path)


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg):
    pofile_path = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    pofile_content = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''

    with open(pofile_path, 'w') as f:
        f.write(pofile_content)

    markdown_content = '# Bar\n'

    pofile, exitcode = run([markdown_content, arg, '-po', pofile_path])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Bar"
msgstr ""
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output

    with open(pofile_path, 'r') as f:
        assert f.read() == expected_output

    os.remove(pofile_path)


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg):
    filesdir = os.path.join(tempfile.gettempdir(), uuid4().hex)

    os.mkdir(filesdir)

    filesdata = {
        'foo': '### Foo\n\nFoo 2',
        'bar': '## Bar with `inline code`',
        'baz': 'baz should not appear'
    }
    for filename, content in filesdata.items():
        filepath = os.path.join(filesdir, filename + '.md')
        with open(filepath, 'w') as f:
            f.write(content)

    _glob = os.path.join(filesdir, '*.md')
    pofile, exitcode = run([_glob, arg, os.path.join(filesdir, 'baz.md')])
    out, err = capsys.readouterr()

    shutil.rmtree(filesdir)

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bar with `inline code`"
msgstr ""

msgid "Foo"
msgstr ""

msgid "Foo 2"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


def test_markuptext(capsys):
    content = ('# Header `with inline code`\n\n'
               'Some text with **bold characters**, *italic characters*'
               ' and a [link](https://nowhere.nothing).\n')

    pofile, exitcode = run([content])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Header `with inline code`"
msgstr ""

msgid ""
"Some text with **bold characters**, *italic characters* and a "
"[link](https://nowhere.nothing)."
msgstr ""
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-w', '--wrapwidth'])
def test_wrapwidth(capsys, arg):
    content = ('# Some long header with **bold characters**, '
               '*italic characters* and a [link](https://nowhere.nothing).\n')
    width = 20

    pofile, exitcode = run([content, arg, str(width), '-p'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid ""
"Some long header "
"with bold "
"characters, italic"
" characters and a "
"link."
msgstr ""
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output

    _line_with_provided_width_found = False
    for line in pofile.__unicode__().split('\n'):
        if len(line) == width:
            _line_with_provided_width_found = True
            break

    assert _line_with_provided_width_found


@pytest.mark.parametrize('arg', ['-o', '--mark-not-found-as-obsolete'])
def test_mark_not_found_as_absolete(capsys, arg):
    old_pofile_path = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    old_pofile_content = '''#
msgid ""
msgstr ""

msgid ""
msgstr "Foo"
'''
    with open(old_pofile_path, 'w') as f:
        f.write(old_pofile_content)

    markdown_content = 'Bar\n'
    pofile, exitcode = run([markdown_content, '-po', old_pofile_path, arg])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr ""

#~ msgid ""
#~ msgstr "Foo"
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-x', '--xheaders'])
def test_xheaders(capsys, arg):
    markdown_content = '# Foo'

    pofile, exitcode = run([markdown_content, arg])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""
"x-mdpo-bold-end: **\\n"
"x-mdpo-bold-start: **\\n"
"x-mdpo-code-end: `\\n"
"x-mdpo-code-start: `\\n"
"x-mdpo-italic-end: *\\n"
"x-mdpo-italic-start: *\\n"
"x-mdpo-latexmath-end: $\\n"
"x-mdpo-latexmath-start: $\\n"
"x-mdpo-latexmathdisplay-end: $$\\n"
"x-mdpo-latexmathdisplay-start: $$\\n"
"x-mdpo-link-end: ]\\n"
"x-mdpo-link-start: [\\n"
"x-mdpo-strikethrough-end: ~~\\n"
"x-mdpo-strikethrough-start: ~~\\n"
"x-mdpo-wikilink-end: ]]\\n"
"x-mdpo-wikilink-start: [[\\n"

msgid "Foo"
msgstr ""
'''

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output
