"""Tests for mdpo text utilities."""

import pytest

from mdpo.text import (
    max_char_in_a_row,
    min_not_max_chars_in_a_row,
    parse_escaped_pair,
)


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


@pytest.mark.parametrize(
    ('text', 'expected_key', 'expected_value', 'expected_error'),
    (
        ('foo:bar', 'foo', 'bar', None),
        ('foo:Bar:', 'foo', 'Bar:', None),
        ('foo:   bar:', 'foo', 'bar:', None),
        ('foo: \n  bar:', 'foo', 'bar:', None),
        ('foo:Bar\\:', 'foo', 'Bar\\:', None),
        ('\\:foo:bar', ':foo', 'bar', None),
        (r'foo\\:Bar:baz', 'foo:Bar', 'baz', None),
        (r'foo\\:Bar:baz\\', 'foo:Bar', r'baz\\', None),
        # : at the beginning means escaped
        (r':foo\\:Bar:baz\\', ':foo:Bar', r'baz\\', None),
        ('foo', None, None, ValueError),
        (':', None, None, ValueError),
        ('', None, None, ValueError),
    ),
)
def test_parse_escaped_pair(
    text,
    expected_key,
    expected_value,
    expected_error,
):
    if expected_error:
        with pytest.raises(expected_error):
            parse_escaped_pair(text)
    else:
        key, value = parse_escaped_pair(text)
        assert key == expected_key
        assert value == expected_value
