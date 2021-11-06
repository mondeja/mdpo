import tempfile
from contextlib import contextmanager

import pytest


@contextmanager
def _tmp_file(content, suffix):
    f = tempfile.NamedTemporaryFile(suffix=suffix)
    f.write(content.encode('utf-8'))
    f.seek(0)
    try:
        yield f.name
    finally:
        f.close()


@pytest.fixture()
def tmp_file():
    return _tmp_file


@pytest.fixture()
def striplastline():
    """Returns a text, ignoring the last line.

    Args:
        text (str): Text that will be returned ignoring its last line.

    Returns:
        str: Text wihout their last line.
    """
    def _striplastline(text):
        stripped_text = '\n'.join(text.split('\n')[:-1])
        if len(stripped_text) == len(text):
            raise Exception('Unnecessary use of \'striplastline\' fixture')
        return stripped_text
    return _striplastline
