import os
import subprocess
import tempfile


def pre_commit_run_all_files(cwd=os.getcwd()):
    return subprocess.run(
        ['pre-commit', 'run', '--all-files'],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_md2po_pre_commit_hook(git_add_commit):
    with tempfile.TemporaryDirectory() as filesdir:
        pre_commit_config_path = os.path.join(
            filesdir,
            '.pre-commit-config.yaml',
        )
        readme_md_path = os.path.join(filesdir, 'README.md')
        readme_po_path = os.path.join(filesdir, 'README.po')

        with open(pre_commit_config_path, 'w') as f:
            f.write('''repos:
  - repo: https://github.com/mondeja/mdpo
    rev: master
    hooks:
      - id: md2po
        files: ^README\\.md
        args:
          - --po-filepath
          - README.po
''')

        with open(readme_md_path, 'w') as f:
            f.write('# Foo\n')
        with open(readme_po_path, 'w') as f:
            f.write('''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
''')

        # first execution, is updated
        proc = subprocess.run(
            ['git', 'init'],
            cwd=filesdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        # second execution, is outdated
        with open(readme_md_path, 'a') as f:
            f.write('\nbar\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )

        with open(readme_po_path) as f:
            assert f.read() == '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""

#: README.md:block 2 (paragraph)
msgid "bar"
msgstr ""
'''


def test_po2md_pre_commit_hook(git_add_commit):
    with tempfile.TemporaryDirectory() as filesdir:
        pre_commit_config_path = os.path.join(
            filesdir,
            '.pre-commit-config.yaml',
        )
        readme_src_md_path = os.path.join(filesdir, 'README.md')
        readme_dst_md_path = os.path.join(filesdir, 'README.es.md')
        readme_po_path = os.path.join(filesdir, 'README.po')

        with open(pre_commit_config_path, 'w') as f:
            f.write('''repos:
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
''')

        with open(readme_src_md_path, 'w') as f:
            f.write('# Foo\n')
        with open(readme_dst_md_path, 'w') as f:
            f.write('# Foo es\n')
        with open(readme_po_path, 'w') as f:
            f.write('''#
msgid ""
msgstr ""

msgid "Foo"
msgstr "Foo es"
''')

        # first execution, is updated
        proc = subprocess.run(
            ['git', 'init'],
            cwd=filesdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        # second execution, is outdated
        with open(readme_src_md_path, 'a') as f:
            f.write('\nbar\n')
        with open(readme_po_path, 'a') as f:
            f.write('\nmsgid "bar"\nmsgstr "bar es"\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )
        with open(readme_dst_md_path) as f:
            assert f.read() == '''# Foo es

bar es
'''


def test_mdpo2html_pre_commit_hook(git_add_commit):
    with tempfile.TemporaryDirectory() as filesdir:
        pre_commit_config_path = os.path.join(
            filesdir,
            '.pre-commit-config.yaml',
        )
        readme_html_path = os.path.join(filesdir, 'README.html')
        readme_html_es_path = os.path.join(filesdir, 'README.es.html')
        readme_po_path = os.path.join(filesdir, 'README.po')

        with open(pre_commit_config_path, 'w') as f:
            f.write('''repos:
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
''')

        with open(readme_html_path, 'w') as f:
            f.write('<h1>Foo</h1>\n')
        with open(readme_html_es_path, 'w') as f:
            f.write('<h1>Foo es</h1>\n')
        with open(readme_po_path, 'w') as f:
            f.write('''#
msgid ""
msgstr ""

msgid "Foo"
msgstr "Foo es"
''')

        # first execution, is updated
        proc = subprocess.run(
            ['git', 'init'],
            cwd=filesdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.returncode == 0

        git_add_commit('First commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')

        with open(readme_html_es_path) as f:
            assert f.read() == '<h1>Foo es</h1>\n'

        # second execution, is outdated
        with open(readme_html_path, 'a') as f:
            f.write('\n<p>bar</p>\n')
        with open(readme_po_path, 'a') as f:
            f.write('\nmsgid "bar"\nmsgstr "bar es"\n')

        git_add_commit('Second commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode != 0

        assert proc.stdout.decode('utf-8').splitlines()[-1] == (
            '- files were modified by this hook'
        )
        with open(readme_html_es_path) as f:
            assert f.read() == '<h1>Foo es</h1>\n\n<p>bar es</p>\n'


def test_md2po2md_pre_commit_hook(git_add_commit):
    with tempfile.TemporaryDirectory() as filesdir:
        pre_commit_config_path = os.path.join(
            filesdir,
            '.pre-commit-config.yaml',
        )
        readme_md_path = os.path.join(filesdir, 'README.md')

        with open(pre_commit_config_path, 'w') as f:
            f.write(
                '''repos:
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
            )

        with open(readme_md_path, 'w') as f:
            f.write('# Foo\n')

        # first execution, files don't exist
        proc = subprocess.run(
            ['git', 'init'],
            cwd=filesdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
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

        with open(readme_po_es_path) as f:
            assert f.read() == '''#
msgid ""
msgstr ""

msgid "Foo"
msgstr ""
'''

        with open(readme_md_es_path) as f:
            assert f.read() == '# Foo\n'

        # second execution, translation
        with open(readme_po_es_path, 'w') as f:
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

        with open(readme_md_es_path) as f:
            assert f.read() == '# Foo es\n'

        # third execution, is updated
        git_add_commit('Third commit', cwd=filesdir)

        proc = pre_commit_run_all_files(cwd=filesdir)
        assert proc.returncode == 0
        assert proc.stdout.decode('utf-8').splitlines()[-1].endswith('Passed')
