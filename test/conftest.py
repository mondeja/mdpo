import tempfile
from contextlib import contextmanager

import pytest


@contextmanager
def _tmp_file(content, suffix):
    f = tempfile.NamedTemporaryFile(suffix=suffix)
    f.write(content.encode("utf-8"))
    f.seek(0)
    try:
        yield f.name
    finally:
        f.close()


@pytest.fixture()
def tmp_file():
    return _tmp_file
