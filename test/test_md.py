"""Tests for mdpo markdown utilities."""

import pytest

from mdpo.md import inline_untexted_links


@pytest.mark.parametrize(
    (
        'text', 'expected_result',
    ),
    (
        ('[https://ever.com]', '<https://ever.com>'),
        ('[Ever](https://ever.com)', '[Ever](https://ever.com)'),
    ),
)
def test_inline_untexted_links__default_parameters(text, expected_result):
    assert inline_untexted_links(text) == expected_result
