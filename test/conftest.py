import os
import tempfile
from contextlib import contextmanager
from uuid import uuid4

import pytest


@contextmanager
def _tmp_pofile(content):
    filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')
    with open(filepath, "w") as f:
        f.write(content)
    try:
        yield filepath
    finally:
        os.remove(filepath)


@pytest.fixture()
def tmp_pofile():
    return _tmp_pofile
