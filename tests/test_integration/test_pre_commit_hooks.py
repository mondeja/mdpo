import os
import subprocess


def pre_commit_run_all_files(cwd=None):
    cwd = cwd or os.getcwd()
    return subprocess.run(
        ['pre-commit', 'run', '--all-files'],
        cwd=cwd,
        capture_output=True,
    )


def test_md2po_pre_commit_hook(tmp_dir, git_init, git_add_commit):
    with tmp_dir([
        (
            '.pre-commit-config.yaml', '''repos:
  - repo: https://github.com/mondeja/mdpo
    rev: master
    hooks:
      - id: md2po
        files: ^README\\.md
        args:
          - --po-filepath
          - README.po
''',
        ),
        ('README.md', '# Foo\n'),
        ('README.po', '#\nmsgid ""\nmsgstr ""\n\nmsgid "Foo"\nmsgstr ""\n'),
    ]) as (filesdir, _, readme_md_path, readme_po_path):
        # first execution, is updated
        proc = git_init(cwd=filesdir)
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        # second execution, is outdated
        with open(readme_md_path, 'a', encoding='utf-8') as f:
            f.write('\nbar\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )

        with open(readme_po_path, encoding='utf-8') as f:
            assert f.read() == '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

#: README.md:block 2 (paragraph)
msgid "bar"
msgstr ""
'''


def test_po2md_pre_commit_hook(tmp_dir, git_init, git_add_commit):
    with tmp_dir([
        (
            '.pre-commit-config.yaml', '''repos:
  - repo: https://github.com/mondeja/mdpo
    rev: master
    hooks:
      - id: po2md
        files: ^README\\.md
        args:
          - -p
          - README.po
          - -s
          - README.es.md
''',
        ),
        ('README.md', '# Foo\n'),
        ('README.es.md', '# Foo es\n'),
        (
            'README.po', '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr "Foo es"
''',
        ),
    ]) as (
        filesdir, _, readme_src_md_path, readme_dst_md_path, readme_po_path,
    ):
        # first execution, is updated
        proc = git_init(cwd=filesdir)
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        # second execution, is outdated
        with open(readme_src_md_path, 'a', encoding='utf-8') as f:
            f.write('\nbar\n')
        with open(readme_po_path, 'a', encoding='utf-8') as f:
            f.write('\nmsgid "bar"\nmsgstr "bar es"\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )
        with open(readme_dst_md_path, encoding='utf-8') as f:
            assert f.read() == '''# Foo es

bar es
'''


def test_mdpo2html_pre_commit_hook(tmp_dir, git_init, git_add_commit):
    with tmp_dir([
        (
            '.pre-commit-config.yaml', '''repos:
  - repo: https://github.com/mondeja/mdpo
    rev: master
    hooks:
      - id: mdpo2html
        files: ^README\\.html
        args:
          - -p
          - README.po
          - -s
          - README.es.html
''',
        ),
        ('README.html', '<h1>Foo</h1>\n'),
        ('README.es.html', '<h1>Foo es</h1>\n'),
        (
            'README.po', '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr "Foo es"
''',
        ),
    ]) as (
        filesdir, _, readme_html_path, readme_html_es_path, readme_po_path,
    ):
        # first execution, is updated
        proc = git_init(cwd=filesdir)
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        with open(readme_html_es_path, encoding='utf-8') as f:
            assert f.read() == '<h1>Foo es</h1>\n'

        # second execution, is outdated
        with open(readme_html_path, 'a', encoding='utf-8') as f:
            f.write('\n<p>bar</p>\n')
        with open(readme_po_path, 'a', encoding='utf-8') as f:
            f.write('\nmsgid "bar"\nmsgstr "bar es"\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )
        with open(readme_html_es_path, encoding='utf-8') as f:
            assert f.read() == '<h1>Foo es</h1>\n\n<p>bar es</p>\n'


def test_md2po2md_pre_commit_hook(tmp_dir, git_init, git_add_commit):
    with tmp_dir({
        '.pre-commit-config.yaml': '''repos:
  - repo: https://github.com/mondeja/mdpo
    rev: master
    hooks:
      - id: md2po2md
        files: ^README\\.md
        args:
          - -l
          - es
          - -o
          - locale/{lang}
          - --no-location
''',
        'README.md': '# Foo\n',
    }) as filesdir:
        # first execution, files don't exist
        proc = git_init(cwd=filesdir)
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 1
        assert proc.stdout.decode('utf-8').splitlines()[-1] == '- exit code: 1'

        locale_dir = os.path.join(filesdir, 'locale')
        assert os.path.isdir(locale_dir)

        locale_es_dir = os.path.join(locale_dir, 'es')
        assert os.path.isdir(locale_es_dir)

        readme_md_es_path = os.path.join(locale_es_dir, 'README.md')
        readme_po_es_path = os.path.join(locale_es_dir, 'README.md.po')
        assert os.path.isfile(readme_md_es_path)
        assert os.path.isfile(readme_po_es_path)

        with open(readme_po_es_path, encoding='utf-8') as f:
            assert f.read() == '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''

        with open(readme_md_es_path, encoding='utf-8') as f:
            assert f.read() == '# Foo\n'

        # second execution, translation
        with open(readme_po_es_path, 'w', encoding='utf-8') as f:
            f.write('''#
msgid ""
msgstr ""

msgid "Foo"
msgstr "Foo es"
''')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 1
        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )

        with open(readme_md_es_path, encoding='utf-8') as f:
            assert f.read() == '# Foo es\n'

        # third execution, is updated
        git_add_commit('Third commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')
