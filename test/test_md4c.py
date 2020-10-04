import pytest

from mdpo.md4c import (
    DEFAULT_MD4C_FLAGS,
    parse_md4c_flags_string,
)

DEFAULT_MODES_OUTPUT = {
    'strikethrough': True,
    'latexmathspans': True,
    'wikilinks': True,
    'underline': False,
}


@pytest.mark.parametrize(('flags_string', 'flags_sum', 'modes'), (
    (
        DEFAULT_MD4C_FLAGS,
        15105,
        DEFAULT_MODES_OUTPUT,
    ),
    (
        DEFAULT_MD4C_FLAGS + '|FOOBARUNEXISTENTFLAGNOTPOSSIBLE',
        15105,
        DEFAULT_MODES_OUTPUT
    ),
    (
        ('MD_FLAG_COLLAPSEWHITESPACE|'
         'MD_FLAG_TABLES|'
         'MD_FLAG_TASKLISTS|'
         'MD_FLAG_WIKILINKS'),
        10497,
        {
            'strikethrough': False,
            'latexmathspans': False,
            'wikilinks': True,
            'underline': False,
        }
    )
))
def test_parse_md4c_flags_string(flags_string, flags_sum, modes):
    flags_sum_result, modes_result = parse_md4c_flags_string(flags_string)
    assert flags_sum_result == flags_sum
    assert modes_result == modes
