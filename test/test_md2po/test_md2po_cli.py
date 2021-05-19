import io
import os
import tempfile

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
''',
}


def test_stdin(capsys, monkeypatch):
    monkeypatch.setattr('sys.stdin', io.StringIO(EXAMPLE['input']))
    pofile, exitcode = run()
    out, err = capsys.readouterr()
    assert exitcode == 0
    assert pofile.__unicode__() == EXAMPLE['output']
    assert striplastline(out) == EXAMPLE['output']


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg):
    pofile, exitcode = run([EXAMPLE['input'], arg])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert pofile.__unicode__() == EXAMPLE['output']
    assert out == ''


@pytest.mark.parametrize('arg', ['-po', '--po-filepath'])
def test_po_filepath(capsys, arg, tmp_file):
    pofile_content = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''
    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Bar"
msgstr ""
'''

    with tmp_file(pofile_content, '.po') as pofile_path:
        pofile, exitcode = run([
            '# Bar\n',
            arg,
            pofile_path,
            '-m',
            '--no-location',
        ])
        out, err = capsys.readouterr()

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-s', '--save'])
def test_save(capsys, arg, tmp_file):
    pofile_content = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''
    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Bar"
msgstr ""
'''

    with tmp_file(pofile_content, '.po') as pofile_path:
        pofile, exitcode = run([
            '# Bar\n',
            arg,
            '-po',
            pofile_path,
            '-m',
            '--no-location',
        ])
        out, err = capsys.readouterr()

        with open(pofile_path) as f:
            assert f.read() == expected_output

    assert exitcode == 0
    assert pofile.__unicode__() == expected_output
    assert striplastline(out) == expected_output


@pytest.mark.parametrize('arg', ['-mo', '--mo-filepath'])
def test_mo_filepath(capsys, arg):
    mo_file = tempfile.NamedTemporaryFile(suffix='.mo')
    mo_filepath = mo_file.name
    mo_file.close()

    pofile, exitcode = run([EXAMPLE['input'], arg, mo_filepath])
    out, err = capsys.readouterr()
    assert exitcode == 0
    assert pofile.__unicode__() == EXAMPLE['output']
    assert striplastline(out) == EXAMPLE['output']
    assert os.path.exists(mo_filepath)

    os.remove(mo_filepath)


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg):
    filesdata = {
        'foo': '### Foo\n\nFoo 2',
        'bar': '## Bar with `inline code`',
        'baz': 'baz should not appear',
    }

    with tempfile.TemporaryDirectory() as filesdir:
        for filename, content in filesdata.items():
            filepath = os.path.join(filesdir, filename + '.md')
            with open(filepath, 'w') as f:
                f.write(content)

        _glob = os.path.join(filesdir, '*.md')
        pofile, exitcode = run([
            _glob,
            arg,
            os.path.join(filesdir, 'bar.md'),
            arg,
            os.path.join(filesdir, 'baz.md'),
            '--no-location',
        ])
        out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
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
    content = (
        '# Header `with inline code`\n\n'
        'Some text with **bold characters**, *italic characters*'
        ' and a [link](https://nowhere.nothing).\n'
    )

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
    content = (
        '# Some long header with **bold characters**, '
        '*italic characters* and a [link](https://nowhere.nothing).\n'
    )
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


@pytest.mark.parametrize('arg', ['-a', '--xheaders'])
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


@pytest.mark.parametrize('arg', ['-c', '--include-codeblocks'])
def test_include_codeblocks(capsys, arg):
    markdown_content = '''
    var hello = "world";

```javascript
var this;
```

This must be included also.
'''
    pofile, exitcode = run([markdown_content, arg])
    out, err = capsys.readouterr()

    expected_output = '''#
msgid ""
msgstr ""

msgid "var hello = \\"world\\";\\n"
msgstr ""

msgid "var this;\\n"
msgstr ""

msgid "This must be included also."
msgstr ""
'''

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('arg', ['--ignore-msgids'])
def test_ignore_msgids(capsys, arg, tmp_file):
    expected_output = '''#
msgid ""
msgstr ""

msgid "bar"
msgstr ""
'''

    with tmp_file('foo\nbaz', '.txt') as filename:
        pofile, exitcode = run(['foo\n\nbar\n\nbaz\n', arg, filename])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('arg', ['--command-alias'])
def test_command_aliases(capsys, arg, tmp_file):
    markdown_content = '''<!-- :off -->
This should be ignored.

<!-- mdpo-on -->

This should be included.

<!-- :off -->

This should be also ignored.
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "This should be included."
msgstr ""
'''

    pofile, exitcode = run([
        markdown_content,
        arg, 'mdpo-on:mdpo-enable',
        arg, '\\:off:mdpo-disable',
    ])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('arg', ['-d', '--metadata'])
def test_metadata(capsys, arg, tmp_file):
    expected_output = '''#
msgid ""
msgstr ""
"Language: es\\n"
"Content-Type: text/plain; charset=utf-8\\n"

msgid "Some content"
msgstr ""
'''

    pofile, exitcode = run([
        'Some content',
        arg, 'Language: es',
        arg, 'Content-Type: text/plain; charset=utf-8',
    ])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('arg', ('-m', '--merge-pofiles'))
def test_merge_pofiles(capsys, arg, tmp_file):
    md_content = '# bar\n\n\nbaz\n'
    pofile_content = '''#
msgid ""
msgstr ""

msgid "foo"
msgstr "foo language"
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "foo"
msgstr "foo language"

msgid "bar"
msgstr ""

msgid "baz"
msgstr ""
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        pofile, exitcode = run([
            md_content,
            '--po-filepath', po_filepath,
            arg,
        ])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('arg', ('-r', '--remove-not-found'))
def test_remove_not_found(capsys, arg, tmp_file):
    md_content = '# bar\n\n\nbaz\n'
    pofile_content = '''#
msgid ""
msgstr ""

msgid "foo"
msgstr "foo language"
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "bar"
msgstr ""

msgid "baz"
msgstr ""
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        pofile, exitcode = run([
            md_content,
            '--po-filepath',
            po_filepath,
            arg,
            '--merge-pofiles',
        ])
    out, err = capsys.readouterr()

    assert exitcode == 0
    assert striplastline(out) == expected_output
    assert pofile.__unicode__() == expected_output
