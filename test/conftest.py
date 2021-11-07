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
