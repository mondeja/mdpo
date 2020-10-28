import glob
import os
import random
import tempfile
from uuid import uuid4

import pytest

from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


EXAMPLES_DIR = os.path.join('test', 'test_md2po', 'extract-examples')


def _build_examples(dirname):
    examples_dir = os.path.join(EXAMPLES_DIR, dirname)
    examples_glob = glob.glob(examples_dir + os.sep + '*.md')
    examples_filenames = sorted([os.path.basename(fp) for fp in examples_glob])
    return (examples_dir, examples_filenames)


EXAMPLES = {}
for suite in os.listdir(EXAMPLES_DIR):
    dirpath, filenames = _build_examples(suite)
    EXAMPLES[suite] = {
        "filenames": filenames,
        "dirpath": dirpath
    }


@pytest.mark.parametrize('filename', EXAMPLES['plaintext']['filenames'])
def test_extract_plaintext(filename):
    filepath = os.path.join(EXAMPLES['plaintext']['dirpath'], filename)
    pofile = markdown_to_pofile(filepath, plaintext=True)

    with open(filepath + '.expect.po', 'r') as expect_file:
        assert pofile.__unicode__() == expect_file.read()


@pytest.mark.parametrize('filename', EXAMPLES['markuptext']['filenames'])
def test_extract_markuptext(filename):
    filepath = os.path.join(EXAMPLES['markuptext']['dirpath'], filename)
    pofile = markdown_to_pofile(filepath, plaintext=False)

    with open(filepath + '.expect.po', 'r') as expect_file:
        assert pofile.__unicode__() == expect_file.read()


@pytest.mark.parametrize('filename', EXAMPLES['underline']['filenames'])
def test_extract_underline(filename):
    filepath = os.path.join(EXAMPLES['underline']['dirpath'], filename)
    pofile = markdown_to_pofile(
        filepath, plaintext=False,
        extensions=DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS + ["underline"])

    with open(filepath + '.expect.po', 'r') as expect_file:
        assert pofile.__unicode__() == expect_file.read()


@pytest.mark.parametrize(
    'filename', [random.choice(EXAMPLES['plaintext']['filenames'])]
)
def test_extract_save(filename):
    filepath = os.path.join(EXAMPLES['plaintext']['dirpath'], filename)

    save_filepath = os.path.join(tempfile.gettempdir(), uuid4().hex + '.po')

    markdown_to_pofile(
        filepath, plaintext=True, save=True, po_filepath=save_filepath)

    with open(filepath + '.expect.po', 'r') as expect_file:
        with open(save_filepath, 'r') as tmpf:
            assert tmpf.read() == expect_file.read()
    os.remove(save_filepath)
