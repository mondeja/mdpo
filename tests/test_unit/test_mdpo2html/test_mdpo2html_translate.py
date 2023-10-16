import glob
import os

import pytest

from mdpo.mdpo2html import markdown_pofile_to_html


EXAMPLES_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'translate-examples',
)


def _build_examples(dirname):
    examples_dir = os.path.join(EXAMPLES_DIR, dirname)
    examples_glob = glob.glob(examples_dir + os.sep + '*.html')
    examples_filenames = sorted(
        os.path.basename(fp) for fp in examples_glob
        if not fp.endswith('.expect.html')
    )
    return (examples_dir, examples_filenames)


EXAMPLES = {}
for suite in os.listdir(EXAMPLES_DIR):
    dirpath, filenames = _build_examples(suite)
    EXAMPLES[suite] = {
        'filenames': filenames,
        'dirpath': dirpath,
    }


@pytest.mark.parametrize('filename', EXAMPLES['markuptext']['filenames'])
def test_translate_markuptext(filename):
    filepath_in = os.path.join(EXAMPLES['markuptext']['dirpath'], filename)
    filepath_out = filepath_in + '.expect.html'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )
    if not os.path.exists(po_filepath):
        po_filepath = ''

    output = markdown_pofile_to_html(filepath_in, po_filepath)

    with open(filepath_out, encoding='utf-8') as f:
        expected_output = f.read()

    assert output == expected_output


@pytest.mark.parametrize(
    'filename',
    EXAMPLES['merge-adjacent-markup']['filenames'],
)
def test_translate_merge_adjacent_markups(filename):
    filepath_in = os.path.join(
        EXAMPLES['merge-adjacent-markup']['dirpath'], filename,
    )
    filepath_out = filepath_in + '.expect.html'
    po_filepath = os.path.join(
        os.path.dirname(filepath_in),
        os.path.splitext(os.path.basename(filepath_in))[0] + '.po',
    )
    if not os.path.exists(po_filepath):
        po_filepath = ''

    output = markdown_pofile_to_html(
        filepath_in, po_filepath,
        merge_adjacent_markups=True,
    )

    with open(filepath_out, encoding='utf-8') as f:
        expected_output = f.read()

    assert output == expected_output
