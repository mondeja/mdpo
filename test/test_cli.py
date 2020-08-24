import os
import shutil
import subprocess
import sys
import tempfile
from uuid import uuid4

import pytest

from md2po.__main__ import run

MARKDOWN_CONTENT_EXAMPLE = {
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


def striplastline(text):
    return '\n'.join(text.split('\n')[:-1])


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg):
    pofile, exitcode = run([MARKDOWN_CONTENT_EXAMPLE['input'], arg])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert pofile.__unicode__() == MARKDOWN_CONTENT_EXAMPLE['output']
    assert out == ''


def test_stdin(capsys, monkeypatch):
    monkeypatch.setattr('sys.stdin', MARKDOWN_CONTENT_EXAMPLE['input'])
    pofile, exitcode = run()
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert pofile.__unicode__() == MARKDOWN_CONTENT_EXAMPLE['output']
    assert striplastline(out) == MARKDOWN_CONTENT_EXAMPLE['output']


@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason="requires Linux platform")
def test_stdin_echo():
    proc = subprocess.Popen(os.path.join('md2po', '__main__.py'),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=b'A line')

    expected_output = '''#
msgid ""
msgstr ""

msgid "A line"
msgstr ""
'''
    assert striplastline(stdout.decode()) == expected_output


@pytest.mark.parametrize('arg', ['-f', '--filepath'])
def test_filepath(capsys, arg):
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

    pofile, exitcode = run([markdown_content, arg, '-f', pofile_path])
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

msgid "Bar with inline code"
msgstr ""

msgid "Foo"
msgstr ""

msgid "Foo 2"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-m', '--markuptext'])
def test_markuptext(capsys, arg):
    content = ('# Header `with inline code`\n\n'
               'Some text with **bold characters**, *italic characters*'
               ' and a [link](https://nowhere.nothing).\n')

    pofile, exitcode = run([content, arg])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Header `with inline code`"
msgstr ""

msgid ""
"Some text with **bold characters**, *italic characters* and a `[link]`."
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

    pofile, exitcode = run([content, arg, str(width)])
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
    pofile, exitcode = run([markdown_content, '-f', old_pofile_path, arg])
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


@pytest.mark.parametrize('arg', ['-fm', '--forbidden-msgids'])
def test_forbidden_msgids(capsys, arg):
    content = '# Foo\n\nBar\n\n## Baz'

    pofile, exitcode = run([content, arg, 'Bar,Baz'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-bs', '--bold-string'])
def test_bold_string(capsys, arg):
    content = 'Text with **bold characters**'

    pofile, exitcode = run([content, arg, '?', '-m'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Text with ?bold characters?"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-is', '--italic-string'])
def test_italic_string(capsys, arg):
    content = 'Text with *italic characters*'

    pofile, exitcode = run([content, arg, '?', '-m'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Text with ?italic characters?"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-cs', '--code-string'])
def test_code_string(capsys, arg):
    content = 'Text with `inline code`'

    pofile, exitcode = run([content, arg, '?', '-m'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Text with ?inline code?"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-lss', '--link-start-string'])
def test_link_start_string(capsys, arg):
    content = 'Text with [a link](link://nowhere)'

    pofile, exitcode = run([content, arg, '?', '-m'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Text with ?a link]`"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-les', '--link-end-string'])
def test_link_end_string(capsys, arg):
    content = 'Text with [a link](link://nowhere)'

    pofile, exitcode = run([content, arg, '?', '-m'])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "Text with `[a link?"
msgstr ""
'''
    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output
