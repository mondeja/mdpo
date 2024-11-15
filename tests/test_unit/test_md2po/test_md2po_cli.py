"""Tests for md2po command line interface."""

import io
import os
import re
import subprocess
import sys

import pytest

from mdpo.compat import importlib_metadata
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


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason='STDIN file not accesible on Windows',
)
def test_stdin_subprocess_input(tmp_file):
    proc = subprocess.run(
        'md2po',
        text=True,
        input=EXAMPLE['input'],
        stdout=subprocess.PIPE,
        check=True,
    )
    assert proc.returncode == 0
    assert proc.stdout == EXAMPLE['output']

    with tmp_file(EXAMPLE['input'], '.md') as mdfile_path:
        proc = subprocess.run(
            ['md2po', '--no-location'],
            text=True,
            input=mdfile_path,
            stdout=subprocess.PIPE,
            check=True,
        )
        assert proc.returncode == 0
        assert proc.stdout == EXAMPLE['output']


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason='STDIN file not accesible on Windows',
)
def test_pipe_redirect_file_stdin(tmp_file):
    with tmp_file(EXAMPLE['input'], '.md') as mdfile_path:
        proc = subprocess.run(  # noqa: DUO116
            f'< {mdfile_path} md2po',
            text=True,
            input=EXAMPLE['input'],
            capture_output=True,
            shell=True,
            check=False,
        )
    assert proc.stdout == EXAMPLE['output']
    assert proc.returncode == 0


def test_mutliple_files(tmp_file, capsys):
    with tmp_file('foo\n', '.md') as foo_path, \
            tmp_file('bar\n', '.md') as bar_path:
        pofile, exitcode = run([foo_path, bar_path])
        stdout, stderr = capsys.readouterr()

        assert exitcode == 0
        assert 'msgid "bar"' in str(pofile)
        assert 'msgid "bar"' in stdout
        assert 'msgid "foo"' in str(pofile)
        assert 'msgid "foo"' in stdout
        assert stderr == ''


def test_multiple_globs(tmp_dir, capsys):
    with tmp_dir({
        'baba.md': 'baba',
        'bar.md': 'bar',
        'baz.md': 'baz',
    }) as filesdir:
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


@pytest.mark.parametrize('arg', ('-q', '--quiet'))
def test_quiet(capsys, arg):
    pofile, exitcode = run([EXAMPLE['input'], arg])
    stdout, stderr = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == EXAMPLE['output']
    assert stdout == ''
    assert stderr == ''


@pytest.mark.parametrize('arg', ('-D', '--debug'))
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
        if line.endswith("msgid=''"):
            assert '\n'.join([*stdout_lines[i + 1:], '']) == EXAMPLE['output']
            po_output_checked = True
            break

    assert po_output_checked


@pytest.mark.parametrize('arg', ('-p', '--po-filepath', '--pofilepath'))
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


@pytest.mark.parametrize('arg', ('-s', '--save'))
def test_save(capsys, arg, tmp_file, tmp_file_path):
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
            '-p',
            pofile_path,
            '-m',
            '--no-location',
        ])

        with open(pofile_path, encoding='utf-8') as f:
            assert f'{f.read()}\n' == expected_output

    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output

    # new PO file creation
    pofile_path = tmp_file_path()
    pofile, exitcode = run([
        '# Bar\n',
        arg,
        '-p',
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
    with open(pofile_path, encoding='utf-8') as f:
        assert f'{f.read()}\n' == expected_output

    stdout, _ = capsys.readouterr()
    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('--mo-filepath', '--mofilepath'))
def test_mo_filepath(capsys, arg, tmp_file):
    with tmp_file(suffix='.mo') as mofile_path:
        pofile, exitcode = run([EXAMPLE['input'], arg, mofile_path])
        stdout, _ = capsys.readouterr()
        assert exitcode == 0
        assert f'{pofile}\n' == EXAMPLE['output']
        assert stdout == EXAMPLE['output']
        assert os.path.exists(mofile_path)


@pytest.mark.parametrize('arg', ('-i', '--ignore'))
def test_ignore_files_by_filepath(tmp_dir, capsys, arg):
    with tmp_dir({
        'foo.md': '### Foo\n\nFoo 2',
        'bar.md': '## Bar with `inline code`',
        'baz.md': 'baz should not appear',
    }) as filesdir:
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


@pytest.mark.parametrize('arg', ('-w', '--wrapwidth'))
@pytest.mark.parametrize('value', ('0', 'inf', 'invalid'))
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
            pofile, exitcode = run([content, arg, value, '--plaintext'])
        stdout, stderr = capsys.readouterr()
        assert stdout == ''
        assert stderr == (
            "Invalid value 'invalid' for -w/--wrapwidth argument.\n"
        )
        return

    pofile, exitcode = run([content, arg, value, '--plaintext'])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('-a', '--xheader'))
def test_xheader(capsys, arg):
    markdown_content = '# Foo'
    expected_output = f'''#
msgid ""
msgstr "X-Generator: mdpo v{importlib_metadata.version("mdpo")}\\n"

msgid "Foo"
msgstr ""

'''

    pofile, exitcode = run([markdown_content, arg])
    stdout, _ = capsys.readouterr()

    assert exitcode == 0
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output


@pytest.mark.parametrize('arg', ('-c', '--include-codeblocks'))
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


@pytest.mark.parametrize('arg', ('--ignore-msgids',))
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


@pytest.mark.parametrize('arg', ('--command-alias',))
def test_command_aliases(capsys, arg):
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


@pytest.mark.parametrize('arg', ('-d', '--metadata'))
def test_metadata(capsys, arg):
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


@pytest.mark.parametrize('arg', ('-e', '--event'))
def test_events(arg, tmp_file, capsys):
    md_content = '# Foo\n\nBaz\n'
    event_file = '''
def transform_text(self, block, text):
    if text == "Foo":
        self.current_msgid = "Bar"
        return False
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bar"
msgstr ""

msgid "Baz"
msgstr ""

'''
    with tmp_file(event_file, '.py') as tmp_filename:
        pofile, exitcode = run([
            md_content,
            arg,
            f'text: {tmp_filename}::transform_text',
        ])
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
    expected_msg = (
        "The argument '-s/--save' does not make sense without passing the"
        " argument '-p/--po-filepath'."
    )

    with pytest.raises(ValueError, match=expected_msg):
        run([EXAMPLE['input'], '--save'])


@pytest.mark.parametrize('arg', ('--no-obsolete',))
def test_no_obsolete(capsys, arg, tmp_file):
    po_input = '''#
msgid ""
msgstr ""

#~ msgid "Hello"
#~ msgstr "Hola"
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bye"
msgstr ""

#~ msgid "Hello"
#~ msgstr "Hola"

'''

    with tmp_file(po_input, '.po') as filename:
        pofile, exitcode = run([arg, '-p', filename, '--no-location', 'Bye'])
    stdout, stderr = capsys.readouterr()

    assert exitcode == 1
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output
    assert stderr == (
        f"Obsolete messages found at {filename} and passed '--no-obsolete'\n"
    )

    po_input = '''#
msgid ""
msgstr ""
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "Bye"
msgstr ""

'''

    with tmp_file(po_input, '.po') as filename:
        pofile, exitcode = run([arg, '-p', filename, '--no-location', 'Bye'])
    stdout, stderr = capsys.readouterr()

    assert exitcode == 1
    assert f'{pofile}\n' == expected_output
    assert stdout == expected_output
    assert stderr == (
        f"Obsolete messages found at {filename} and passed '--no-obsolete'\n"
    )
