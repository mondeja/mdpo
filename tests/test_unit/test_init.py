import importlib

import pytest


def test_pep562():
    # __getattr__
    mdpo = importlib.import_module('mdpo')
    assert mdpo.markdown_to_pofile is importlib.import_module(
        'mdpo.md2po',
    ).markdown_to_pofile

    expected_msg = "cannot import name 'foobarbaz' from 'mdpo'"
    with pytest.raises(ImportError, match=expected_msg):
        mdpo.foobarbaz  # noqa: B018
