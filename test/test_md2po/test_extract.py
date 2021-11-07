import glob
import os
import random
import tempfile

import pytest

from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


EXAMPLES_DIR = os.path.join('test', 'test_md2po', 'extract-examples')


def _build_examples(dirname):
    examples_dir = os.path.join(EXAMPLES_DIR, dirname)
    examples_glob = glob.glob(os.path.join(examples_dir, '*.md'))
    examples_filenames = sorted(os.path.basename(fp) for fp in examples_glob)
    return (examples_dir, examples_filenames)


EXAMPLES = {}
for suite in os.listdir(EXAMPLES_DIR):
    dirpath, filenames = _build_examples(suite)
    EXAMPLES[suite] = {
        'filenames': filenames,
        'dirpath': dirpath,
    }


@pytest.mark.parametrize('filename', EXAMPLES['plaintext']['filenames'])
def test_extract_plaintext(filename):
    filepath = os.path.join(EXAMPLES['plaintext']['dirpath'], filename)
    pofile = markdown_to_pofile(filepath, plaintext=True, location=False)

    with open(f'{filepath}.expect.po') as expect_file:
        assert str(pofile) == expect_file.read()


@pytest.mark.parametrize('filename', EXAMPLES['markuptext']['filenames'])
def test_extract_markuptext(filename):
    filepath = os.path.join(EXAMPLES['markuptext']['dirpath'], filename)
    pofile = markdown_to_pofile(filepath, plaintext=False, location=False)

    with open(f'{filepath}.expect.po') as expect_file:
        assert str(pofile) == expect_file.read()


@pytest.mark.parametrize('filename', EXAMPLES['underline']['filenames'])
def test_extract_underline(filename):
    filepath = os.path.join(EXAMPLES['underline']['dirpath'], filename)
    pofile = markdown_to_pofile(
        filepath,
        plaintext=False,
        extensions=DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS + ['underline'],
        location=False,
    )

    with open(f'{filepath}.expect.po') as expect_file:
        assert str(pofile) == expect_file.read()


@pytest.mark.parametrize(
    'filename', [random.choice(EXAMPLES['plaintext']['filenames'])],
)
def test_extract_save(filename):
    filepath = os.path.join(EXAMPLES['plaintext']['dirpath'], filename)

    with tempfile.NamedTemporaryFile(suffix='.po') as save_file:

        markdown_to_pofile(
            filepath,
            plaintext=True,
            save=True,
            po_filepath=save_file.name,
            location=False,
        )

        with open(f'{filepath}.expect.po') as expect_file:
            assert save_file.read().decode('utf-8') == expect_file.read()
