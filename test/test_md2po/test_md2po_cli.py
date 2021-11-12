"""Tests for md2po command line interface."""

import io
import os
import re
import subprocess
import sys
import tempfile
import uuid

import pytest

from mdpo.md2po.__main__ import run


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
    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == EXAMPLE['output']
    assert stdout == EXAMPLE['output']


def test_stdin_subprocess_input(tmp_file):
    proc = subprocess.run(
        'md2po',
        universal_newlines=True,
        input=EXAMPLE['input'],
        stdout=subprocess.PIPE,
        check=True,
    )
    assert proc.returncode == 0
    assert proc.stdout == EXAMPLE['output']

    with tmp_file(EXAMPLE['input'], '.md') as mdfile_path:
        proc = subprocess.run(
            ['md2po', '--no-location'],
            universal_newlines=True,
            input=mdfile_path,
            stdout=subprocess.PIPE,
            check=True,
        )
        assert proc.returncode == 0
        assert proc.stdout == EXAMPLE['output']


@pytest.mark.skipif(sys.platform != 'linux', reason='Linux only test')
def test_pipe_redirect_file_stdin(tmp_file):
    with tmp_file(EXAMPLE['input'], '.md') as mdfile_path:
        proc = subprocess.run(
            f'< {mdfile_path} md2po',
            universal_newlines=True,
            input=EXAMPLE['input'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
    assert proc.stdout == EXAMPLE['output']
    assert proc.returncode == 0


def test_mutliple_files(tmp_file, capsys):
    with tmp_file('foo\n', '.md') as foo_path, \
            tmp_file('bar\n', '.md') as bar_path:
        pofile, exitcode = run([foo_path, bar_path])
        stdout, stderr = capsys.readouterr()

        assert exitcode == 0
        assert len(f'{pofile}\n'.splitlines()) == 12
        assert len(stdout.splitlines()) == 12
        assert 'msgid "bar"' in str(pofile)
        assert 'msgid "bar"' in stdout
        assert 'msgid "foo"' in str(pofile)
        assert 'msgid "foo"' in stdout
        assert stderr == ''


def test_multiple_globs(capsys):
    filesdata = {
        'baba': 'baba',
        'bar': 'bar',
        'baz': 'baz',
    }

    with tempfile.TemporaryDirectory() as filesdir:
        for filename, content in filesdata.items():
            with open(os.path.join(filesdir, f'{filename}.md'), 'w') as f:
                f.write(content)

        pofile, exitcode = run([
            os.path.join(filesdir, 'ba*.md'),
            os.path.join(filesdir, 'bab*.md'),
            '--no-location',
        ])
        stdout, stderr = capsys.readouterr()

        expected_output = '''#
msgid ""
msgstr ""

msgid "baba"
msgstr ""

msgid "bar"
msgstr ""

msgid "baz"
msgstr ""

'''

        assert exitcode == 0
        assert f'{pofile}\n' == expected_output
        assert stdout == expected_output
        assert stderr == ''


@pytest.mark.parametrize('arg', ['-q', '--quiet'])
def test_quiet(capsys, arg):
    pofile, exitcode = run([EXAMPLE['input'], arg])
    stdout, stderr = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == EXAMPLE['output']
    assert stdout == ''
    assert stderr == ''


@pytest.mark.parametrize('arg', ['-D', '--debug'])
def test_debug(capsys, arg):
    pofile, exitcode = run([EXAMPLE['input'], arg])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == EXAMPLE['output']

    po_output_checked = False

    stdout_lines = stdout.splitlines()
    for i, line in enumerate(stdout_lines):
        assert re.match(
            (
                r'^md2po\[DEBUG\]::\d{4,}-\d\d-\d\d\s\d\d:\d\d:\d\d\.\d+::'
                r'(text|link_reference|msgid|command|enter_block|'
                r'leave_block|enter_span|leave_span)::'
            ),
            line,
        )
        if line.endswith('msgid=\'\''):
            assert '\n'.join([*stdout_lines[i + 1:], '']) == EXAMPLE['output']
            po_output_checked = True
            break

    assert po_output_checked


@pytest.mark.parametrize('arg', ['-po', '--po-filepath', '--pofilepath'])
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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


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

        with open(pofile_path) as f:
            assert f'{f.read()}\n' == expected_output

    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output

    # new PO file creation
    pofile_path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex[:8])
    pofile, exitcode = run([
        '# Bar\n',
        arg,
        '-po',
        pofile_path,
        '-m',
        '--no-location',
    ])

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr ""

'''
    with open(pofile_path) as f:
        assert f'{f.read()}\n' == expected_output

    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ['-mo', '--mo-filepath', '--mofilepath'])
def test_mo_filepath(capsys, arg):
    with tempfile.NamedTemporaryFile(suffix='.mo') as mo_file:
        pofile, exitcode = run([EXAMPLE['input'], arg, mo_file.name])
        stdout, _ = capsys.readouterr()
        assert exitcode == 0
        assert f'{pofile}\n' == EXAMPLE['output']
        assert stdout == EXAMPLE['output']
        assert os.path.exists(mo_file.name)


@pytest.mark.parametrize('arg', ['-i', '--ignore'])
def test_ignore_files_by_filepath(capsys, arg):
    filesdata = {
        'foo': '### Foo\n\nFoo 2',
        'bar': '## Bar with `inline code`',
        'baz': 'baz should not appear',
    }

    with tempfile.TemporaryDirectory() as filesdir:
        for filename, content in filesdata.items():
            with open(os.path.join(filesdir, f'{filename}.md'), 'w') as f:
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

    expected_output = '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Foo 2"
msgstr ""

'''

    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


def test_markuptext(capsys):
    content = (
        '# Header `with inline code`\n\n'
        'Some text with **bold characters**, *italic characters*'
        ' and a [link](https://nowhere.nothing).\n'
    )

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

    pofile, exitcode = run([content])
    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ['-w', '--wrapwidth'])
@pytest.mark.parametrize('value', ['0', 'inf', 'invalid'])
def test_wrapwidth(capsys, arg, value):
    content = (
        '# Some long header with **bold characters**, '
        '*italic characters* and a [link](https://nowhere.nothing).\n'
    )
    expected_output = '''#
msgid ""
msgstr ""

msgid "Some long header with bold characters, italic characters and a link."
msgstr ""

'''

    if value == 'invalid':
        with pytest.raises(SystemExit):
            pofile, exitcode = run([content, arg, value, '-p'])
        stdout, stderr = capsys.readouterr()
        assert stdout == ''
        assert stderr == (
            'Invalid value \'invalid\' for -w/--wrapwidth argument.\n'
        )
        return

    pofile, exitcode = run([content, arg, value, '-p'])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ['-a', '--xheaders'])
def test_xheaders(capsys, arg):
    markdown_content = '# Foo'
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
"x-mdpo-strikethrough-end: ~~\\n"
"x-mdpo-strikethrough-start: ~~\\n"
"x-mdpo-wikilink-end: ]]\\n"
"x-mdpo-wikilink-start: [[\\n"

msgid "Foo"
msgstr ""

'''

    pofile, exitcode = run([markdown_content, arg])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ['-c', '--include-codeblocks'])
def test_include_codeblocks(capsys, arg):
    markdown_content = '''
    var hello = "world";

```javascript
var this;
```

This must be included also.
'''

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

    pofile, exitcode = run([markdown_content, arg])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('-m', '--merge-pofiles', '--merge-po-files'))
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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


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
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('-x', '--extension', '--ext'))
@pytest.mark.parametrize(
    ('extensions', 'md_content', 'expected_output'),
    (
        pytest.param(
            None,
            '''| Foo | Bar |
| :-: | :-: |
| Baz | Qux |
''',
            '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

msgid "Bar"
msgstr ""

msgid "Baz"
msgstr ""

msgid "Qux"
msgstr ""

''',
            id='tables (included by default)',
        ),
        pytest.param(
            ['strikethrough'],
            '''| Foo | Bar |
| :-: | :-: |
| Baz | Qux |
''',
            '''#
msgid ""
msgstr ""

msgid "| Foo | Bar | | :-: | :-: | | Baz | Qux |"
msgstr ""

''',
            id='strikethrough (overwrite default extensions)',
        ),
    ),
)
def test_extensions(
    arg,
    extensions,
    md_content,
    expected_output,
    capsys,
):
    extensions_arguments = []
    if extensions:
        for extension in extensions:
            extensions_arguments.extend([arg, extension])

    pofile, exitcode = run([md_content, *extensions_arguments])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize(
    'value',
    (None, 'foo'),
    ids=('_MDPO_RUNNING=', '_MDPO_RUNNING=foo'),
)
def test_md2po_cli_running_osenv(value, capsys):
    if value is not None:
        os.environ['_MDPO_RUNNING'] = value
    pofile, exitcode = run([EXAMPLE['input']])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == EXAMPLE['output']
    assert stdout == EXAMPLE['output']
    assert os.environ.get('_MDPO_RUNNING') == value


def test_md2po_save_without_po_filepath():
    with pytest.raises(ValueError) as exc:
        run([EXAMPLE['input'], '--save'])

    assert str(exc.value) == (
        "The argument '-s/--save' does not make sense without passing the"
        " argument '-po/--po-filepath'."
    )
