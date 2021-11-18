import importlib
import sys

import pytest


@pytest.mark.skipif(
    sys.version_info < (3, 7),
    reason='PEP562 was implemented in Python 3.7',
)
def test_pep562():
    # __getattr__
    mdpo = importlib.import_module('mdpo')
    assert getattr(mdpo, 'markdown_to_pofile') is getattr(
        importlib.import_module('mdpo.md2po'),
        'markdown_to_pofile',
    )

    expected_msg = 'cannot import name \'foobarbaz\' from \'mdpo\''
    with pytest.raises(ImportError, match=expected_msg):
        getattr(mdpo, 'foobarbaz')

    # __dir__
    assert dir(mdpo) == [
        '__description__',
        '__title__',
        '__version__',
        'markdown_pofile_to_html',
        'markdown_to_pofile',
        'markdown_to_pofile_to_markdown',
        'pofile_to_markdown',
    ]
