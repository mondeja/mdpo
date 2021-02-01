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
        (
            'String with [self-referenced-link]',
            'String with <self-referenced-link>',
        ),
        (
            'String with [self-referenced-link]and letter continuation',
            'String with <self-referenced-link>and letter continuation',
        ),
        (
            'String with [self-referenced-link] and space continuation',
            'String with <self-referenced-link> and space continuation',
        ),

        # does not replaces if character that continues is a ``[`` (limitation)
        (
            'String with [self-referenced-link][and malformatted link',
            'String with [self-referenced-link][and malformatted link',
        ),
    ),
)
def test_inline_untexted_links__default_parameters(text, expected_result):
    assert inline_untexted_links(text) == expected_result
