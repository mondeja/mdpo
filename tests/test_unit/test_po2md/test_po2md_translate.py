import glob
import os

import pytest

from mdpo.md2po import markdown_to_pofile
from mdpo.po2md import pofile_to_markdown


EXAMPLES_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'translate-examples',
)
EXAMPLES = sorted(
    os.path.basename(fp) for fp in glob.glob(EXAMPLES_DIR + os.sep + '*.md')
    if not fp.endswith('.expect.md')
)


@pytest.mark.parametrize('filename', EXAMPLES)
def test_translate_markuptext(filename):
    filepath_in = os.path.join(EXAMPLES_DIR, filename)
    filepath_out = filepath_in + '.expect.md'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )

    # assert reference PO file content
    pofile = markdown_to_pofile(
        filepath_in, location=False, po_filepath=po_filepath,
    )

    with open(po_filepath) as f:
        pofile_content = f.read()
    assert str(pofile) == pofile_content

    # assert translation
    output = pofile_to_markdown(filepath_in, po_filepath)
    with open(filepath_out) as f:
        expected_output = f.read()
    assert output == expected_output


@pytest.mark.parametrize('filename', (EXAMPLES[0],))
def test_translate_save(filename, tmp_file):
    filepath_in = os.path.join(EXAMPLES_DIR, filename)
    filepath_out = filepath_in + '.expect.md'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )

    with tmp_file(suffix='.po') as save_filepath:
        pofile_to_markdown(filepath_in, po_filepath, save=save_filepath)

        with open(save_filepath) as f:
            result = f.read()

        with open(filepath_out) as expect_file:
            assert result == expect_file.read()
