import pytest

from mdpo.po import po_escaped_string


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
def test_po_escaped_string(string, escaped):
    assert po_escaped_string(string) == escaped
