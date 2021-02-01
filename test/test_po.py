import pytest

from mdpo.po import build_po_escaped_string


@pytest.mark.parametrize(
    ('string', 'escaped'), (
        ('**', '\\*'),
        ('*', '\\*'),
        ('`[', '\\`'),
        ('jfsakjbfjksafs', '\\j'),
        ('\\n', '\\\\'),
        ('\n', '\\\n'),
    ),
)
def test_build_po_escaped_string(string, escaped):
    assert build_po_escaped_string(string) == escaped
