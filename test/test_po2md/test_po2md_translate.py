import glob
import os
import random
import tempfile

import pytest

from mdpo.po2md import pofile_to_markdown


EXAMPLES_DIR = os.path.join('test', 'test_po2md', 'translate-examples')


def _build_examples(dirname):
    examples_dir = os.path.join(EXAMPLES_DIR, dirname)
    examples_glob = glob.glob(examples_dir + os.sep + '*.md')
    examples_filenames = sorted([
        os.path.basename(fp) for fp in examples_glob
        if not fp.endswith(".expect.md")
    ])
    return (examples_dir, examples_filenames)


EXAMPLES = {}
for suite in os.listdir(EXAMPLES_DIR):
    dirpath, filenames = _build_examples(suite)
    EXAMPLES[suite] = {
        "filenames": filenames,
        "dirpath": dirpath,
    }


@pytest.mark.parametrize('filename', EXAMPLES['markuptext']['filenames'])
def test_translate_markuptext(filename):
    filepath_in = os.path.join(EXAMPLES['markuptext']['dirpath'], filename)
    filepath_out = filepath_in + '.expect.md'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )

    output = pofile_to_markdown(filepath_in, po_filepath)

    with open(filepath_out) as f:
        expected_output = f.read()

    assert output == expected_output


@pytest.mark.parametrize(
    'filename', [random.choice(EXAMPLES['markuptext']['filenames'])],
)
def test_translate_save(filename):
    filepath_in = os.path.join(EXAMPLES['markuptext']['dirpath'], filename)
    filepath_out = filepath_in + '.expect.md'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )

    save_file = tempfile.NamedTemporaryFile(suffix=".po")

    pofile_to_markdown(filepath_in, po_filepath, save=save_file.name)
    save_file.seek(0)

    with open(filepath_out) as expect_file:
        assert save_file.read().decode("utf-8") == expect_file.read()
    save_file.close()
