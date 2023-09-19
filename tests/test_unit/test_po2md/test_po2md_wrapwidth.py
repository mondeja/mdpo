"""Wrapping rendering tests for ``po2md`` CLI."""

import glob
import math
import os

import pytest
from mdpo.po2md import pofile_to_markdown


EXAMPLES_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'wrapwidth-examples',
)
EXAMPLES = sorted(
    os.path.basename(fp) for fp in glob.glob(EXAMPLES_DIR + os.sep + '*.md')
    if not fp.endswith('.expect.md')
)


@pytest.mark.parametrize('wrapwidth', (10, 40, 80, 2000, 0, math.inf))
@pytest.mark.parametrize('filename', EXAMPLES)
def test_wrapwidth(filename, wrapwidth):
    filepath_in = os.path.join(EXAMPLES_DIR, filename)
    wrapwidth = wrapwidth if wrapwidth != math.inf else 'inf'
    filepath_out = f'{filepath_in}.{wrapwidth}.expect.md'

    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )

    output = pofile_to_markdown(filepath_in, po_filepath, wrapwidth=wrapwidth)

    with open(filepath_out, encoding='utf-8') as f:
        expected_output = f.read()
    assert output == expected_output
