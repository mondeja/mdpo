"""Tests for mdpo text utilities."""

import pytest

from mdpo.text import max_char_in_a_row, min_not_max_chars_in_a_row


@pytest.mark.parametrize(
    ('char', 'text', 'expected_result'), (
        ('`', 'hello `` ``` a `` `', 3),
        ('`', 'hello `` ``` a ```` `', 4),
        ('`', 'hello `` ``` a `` `````', 5),

        # does not work for multiple characters
        ('``', 'hello `` ``` a `` `````', 0),
    ),
)
def test_max_char_in_a_row(char, text, expected_result):
    assert max_char_in_a_row(char, text) == expected_result


@pytest.mark.parametrize(
    ('char', 'text', 'expected_result'), (
        ('`', 'hello `` ``` a `` `', 4),
        ('`', 'hello `` ``` a ```` `', 5),
        ('`', 'hello `` ``` a `` `````', 1),
        ('`', 'hello ` `` ``` a `` `````', 4),

        # as default, 1
        ('`', 'hello', 1),

        # does not work for multiple characters (returns default)
        ('``', 'hello `` ``` a `` `````', 1),
    ),
)
def test_min_not_max_chars_in_a_row(char, text, expected_result):
    assert min_not_max_chars_in_a_row(char, text) == expected_result
