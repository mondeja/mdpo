import glob
import os
import random
import tempfile
from uuid import uuid4

import pytest

from md2po import markdown_to_pofile

EXAMPLES_DIR = os.path.join('test', 'convert-examples')

PT_EXAMPLES_DIR = os.path.join(EXAMPLES_DIR, 'plaintext')
PT_EXAMPLES_GLOB = glob.glob(PT_EXAMPLES_DIR + os.sep + '*.md')
PT_EXAMPLES = sorted([os.path.basename(fp) for fp in PT_EXAMPLES_GLOB])

MT_EXAMPLES_DIR = os.path.join(EXAMPLES_DIR, 'markuptext')
MT_EXAMPLES_GLOB = glob.glob(MT_EXAMPLES_DIR + os.sep + '*.md')
MT_EXAMPLES = sorted([os.path.basename(fp) for fp in MT_EXAMPLES_GLOB])


@pytest.mark.parametrize('filename', PT_EXAMPLES)
def test_convert_plaintext(filename):
    filepath = os.path.join(PT_EXAMPLES_DIR, filename)
    pofile = markdown_to_pofile(filepath, plaintext=True)

    with open(filepath + '.expect.po', 'r') as expect_file:
        assert pofile.__unicode__() == expect_file.read()


@pytest.mark.parametrize('filename', MT_EXAMPLES)
def test_convert_markuptext(filename):
    filepath = os.path.join(MT_EXAMPLES_DIR, filename)
    pofile = markdown_to_pofile(filepath, plaintext=False)

    with open(filepath + '.expect.po', 'r') as expect_file:
        assert pofile.__unicode__() == expect_file.read()


@pytest.mark.parametrize('filename', [random.choice(PT_EXAMPLES)])
def test_convert_save(filename):
    filepath = os.path.join(PT_EXAMPLES_DIR, filename)

    save_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')

    markdown_to_pofile(
        filepath, plaintext=True, save=True, po_filepath=save_filepath)

    with open(filepath + '.expect.po', 'r') as expect_file:
        with open(save_filepath, 'r') as tmpf:
            assert tmpf.read() == expect_file.read()
