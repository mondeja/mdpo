import os
import subprocess
import tempfile
from contextlib import contextmanager

import pytest


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
