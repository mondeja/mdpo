"""Tests for mdpo text utilities."""

import math

import pytest

from mdpo.text import (
    min_not_max_chars_in_a_row,
    parse_escaped_pair,
    parse_strint_0_inf,
    parse_wrapwidth_argument,
)


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
    ('text', 'expected_result'),
    (
        ('foo:bar', ('foo', 'bar')),
        ('foo:Bar:', ('foo', 'Bar:')),
        ('foo:   bar:', ('foo', 'bar:')),
        ('foo: \n  bar:', ('foo', 'bar:')),
        ('foo:Bar\\:', ('foo', 'Bar\\:')),
        ('\\:foo:bar', (':foo', 'bar')),
        (r'foo\\:Bar:baz', ('foo:Bar', 'baz')),
        (r'foo\\:Bar:baz\\', ('foo:Bar', r'baz\\')),
        # : at the beginning means escaped
        (r':foo\\:Bar:baz\\', (':foo:Bar', r'baz\\')),
        ('foo', ValueError),
        (':', ValueError),
        ('', ValueError),
    ),
)
def test_parse_escaped_pair(text, expected_result, maybe_raises):
    with maybe_raises(expected_result):
        key, value = parse_escaped_pair(text)
        expected_key, expected_value = expected_result
        assert key == expected_key
        assert value == expected_value


@pytest.mark.parametrize(
    ('value', 'expected_result'),
    (
        ('1', 1),
        ('1.1', 1),
        (-1, math.inf),
        (-1.1, math.inf),
        ('-1', math.inf),
        ('-1.1', math.inf),
        (0, math.inf),
        (-0, math.inf),
        ('a', ValueError),
        ('nan', ValueError),
        ('NotANumber', ValueError),
        ('inf', math.inf),
        ('InF', math.inf),
        ('-inf', math.inf),
        ('-iNf', math.inf),
        ('iNfInItY', math.inf),
        ('+1E6', 1000000),
    ),
)
def test_parse_strint_0_inf(value, expected_result, maybe_raises):
    with maybe_raises(expected_result):
        assert parse_strint_0_inf(value) == expected_result


@pytest.mark.parametrize(
    'value', ('0', '80', 'inf', 'infinity', 'nan', 'invalid'),
)
def test_parse_wrapwidth_argument(value):
    if not value.isdigit() and value.lower() not in ('inf', 'infinity'):
        expected_msg = f'Invalid value \'{value}\' for wrapwidth argument.'
        with pytest.raises(ValueError, match=expected_msg):
            parse_wrapwidth_argument(value)
    else:
        assert parse_wrapwidth_argument(value) == (
            float('inf') if float(value) == 0 else float(value)
        )
