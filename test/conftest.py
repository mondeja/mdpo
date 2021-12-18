"""mdpo tests configuration."""

import ast
import inspect
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager

import pytest


AST_ELTS_VALUE_ATTR = 's' if sys.version_info < (3, 8) else 'value'


@contextmanager
def _tmp_file(content, suffix):
    with tempfile.NamedTemporaryFile(suffix=suffix) as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        yield f.name


@pytest.fixture()
def tmp_file():
    return _tmp_file


@pytest.fixture()
def git_add_commit():
    def _git_add_commit(message, files='.', cwd=os.getcwd()):
        add_proc = subprocess.run(
            ['git', 'add', files],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        commit_proc = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return add_proc.returncode == 0 and commit_proc.returncode == 0
    return _git_add_commit


@pytest.fixture()
def class_slots():
    def get_class_slots(code):
        class ClassSlotsExtractor(ast.NodeVisitor):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.slots = []

            def visit_ClassDef(self, node):
                for children in node.body:
                    if (
                        isinstance(children, ast.Assign)
                        and children.targets[0].id == '__slots__'
                    ):
                        self.slots.extend([
                            getattr(elt, AST_ELTS_VALUE_ATTR)
                            for elt in children.value.elts
                        ])
                        break

        modtree = ast.parse(inspect.getsource(code))
        visitor = ClassSlotsExtractor()
        visitor.visit(modtree)
        return visitor.slots
    return get_class_slots
