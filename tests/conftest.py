"""mdpo tests configuration."""

import ast
import contextlib
import inspect
import os
import subprocess
import sys
import tempfile
import uuid

import pytest


rootdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
temporal_dir = os.path.join(rootdir, 'temp')
if not os.path.isdir(temporal_dir):
    os.mkdir(temporal_dir)

tests_dir = os.path.join(rootdir, 'tests')
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)


@contextlib.contextmanager
def _tmp_file(content='', suffix=''):
    filepath = _tmp_file_path(suffix=suffix)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        f.seek(0)
        yield filepath


@pytest.fixture
def tmp_file():
    return _tmp_file


def _tmp_file_path(suffix=''):
    return os.path.join(temporal_dir, f'{uuid.uuid4().hex[:8]}{suffix}')


@pytest.fixture
def tmp_file_path():
    return _tmp_file_path


def _create_tmpdir_file(tmpdir, file_relpath, content):
    filepath = os.path.join(tmpdir, file_relpath)
    file_parent_dir = os.path.abspath(os.path.dirname(filepath))
    os.makedirs(file_parent_dir, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


@contextlib.contextmanager
def _tmp_dir(files_contents):
    with tempfile.TemporaryDirectory() as tmpdir:
        if isinstance(files_contents, dict):
            # build files with dict, only yields top directory
            for file_relpath, content in files_contents.items():
                _create_tmpdir_file(tmpdir, file_relpath, content)
            yield tmpdir
        elif isinstance(files_contents, list):
            # build files with list, yields all files paths
            filepaths = []
            for file_relpath, content in files_contents:
                filepaths.append(
                    _create_tmpdir_file(tmpdir, file_relpath, content),
                )
            yield (tmpdir, *filepaths)


@pytest.fixture
def tmp_dir():
    return _tmp_dir


def _git_init(cwd=None):
    return subprocess.run(
        ['git', 'init'],
        cwd=cwd,
        capture_output=True,
    )


@pytest.fixture
def git_init():
    return _git_init


@pytest.fixture
def git_add_commit():
    def _git_add_commit(message, files='.', cwd=None):
        cwd = cwd or os.getcwd()
        add_proc = subprocess.run(
            ['git', 'add', files],
            cwd=cwd,
            capture_output=True,
        )

        commit_proc = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=cwd,
            capture_output=True,
        )

        return not any([add_proc.returncode, commit_proc.returncode])
    return _git_add_commit


def get_class_slots(code):
    class ClassSlotsExtractor(ast.NodeVisitor):
        ast_elts_value_attr = (
            's' if sys.version_info < (3, 8) else 'value'
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.slots = []

        def visit_ClassDef(self, node):
            for child in node.body:
                if (
                    isinstance(child, ast.Assign)
                    and child.targets[0].id == '__slots__'
                ):
                    self.slots.extend([
                        getattr(elt, self.ast_elts_value_attr)
                        for elt in child.value.elts
                    ])
                    break

    modtree = ast.parse(inspect.getsource(code))
    visitor = ClassSlotsExtractor()
    visitor.visit(modtree)
    return visitor.slots


@pytest.fixture
def class_slots():
    return get_class_slots


def _wrap_location_comment(filepath, rest):
    target_type, number, context = rest.split(' ', 2)
    result = f'#: {filepath}:{target_type}'
    if len(result) > 76:
        result += f'\n#: {number}'
    else:
        if len(result) + len(number) > 79:
            result += f'\n#: {number}'
        else:
            result += f' {number}'
            if len(result) > 80:
                result += '\n#:'
    result += f' {context}'
    return result


@pytest.fixture
def wrap_location_comment():
    return _wrap_location_comment
