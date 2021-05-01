"""HTML mdpo command utitlites tests."""

import pytest

from mdpo.command import (
    get_valid_mdpo_command_names,
    normalize_mdpo_command,
    normalize_mdpo_command_aliases,
    parse_mdpo_html_command,
)
from mdpo.text import removeprefix


@pytest.mark.parametrize(
    ('value', 'expected_command', 'expected_comment'), (
        ('<!-- mdpo-include-codeblock -->', 'mdpo-include-codeblock', None),
        ('<!-- mdpo_include_codeblock -->', 'mdpo_include_codeblock', None),
        ('<!-- -->', None, None),

        # comments include spaces at the end, implementations must rstrip them
        ('<!-- mdpo-include Hello world -->', 'mdpo-include', 'Hello world '),
        ('<!--mdpo-include Hello world-->', 'mdpo-include', 'Hello world'),
        ('<!-- mdpo-include Hello world-->', 'mdpo-include', 'Hello world'),
        (
            '<!-- mdpo-include Hello world\n-->',
            'mdpo-include',
            'Hello world\n',
        ),
        (
            '<!-- mdpo-include Hello world\n -->',
            'mdpo-include',
            'Hello world\n ',
        ),
        ('<!--mdpo-includeHello world-->', 'mdpo-includeHello', 'world'),
        ('<!--mdpo_include Hello world-->', 'mdpo_include', 'Hello world'),
    ),
)
def test_parse_mdpo_html_command(value, expected_command, expected_comment):
    command, comment = parse_mdpo_html_command(value)
    assert command == expected_command
    assert comment == expected_comment


@pytest.mark.parametrize(
    ('value', 'expected_command'), (
        ('include-codeblock', 'mdpo-include-codeblock'),
        ('include_codeblock', None),
        ('include', 'mdpo-include'),
        ('mdpo-include', 'mdpo-include'),
        ('mdpo-mdpo-include', None),
    ),
)
def test_normalize_mdpo_command(value, expected_command):
    assert normalize_mdpo_command(value) == expected_command


@pytest.mark.parametrize(
    ('command_aliases', 'expected_result'), (
        (
            {'inclusion': 'mdpo-include'},
            {'inclusion': 'mdpo-include'},
        ),
        (
            {'mdpo-inclusion': 'mdpo-include'},
            {'mdpo-inclusion': 'mdpo-include'},
        ),
        (
            {'inclusion': 'include'},
            {'inclusion': 'mdpo-include'},
        ),
        (
            {'inclusion': 'inclusion'},
            ValueError,
        ),
    ),
)
def test_normalize_mdpo_command_aliases(command_aliases, expected_result):
    if hasattr(expected_result, '__traceback__'):
        with pytest.raises(expected_result):
            normalize_mdpo_command_aliases(command_aliases)
    else:
        assert normalize_mdpo_command_aliases(
            command_aliases,
        ) == expected_result


def test_get_valid_mdpo_command_names():
    valid_command_names = get_valid_mdpo_command_names()

    for command_name in valid_command_names:
        assert command_name
        assert isinstance(command_name, str)

        if command_name.startswith('mdpo-'):
            assert removeprefix(command_name, 'mdpo-') in valid_command_names
        else:
            assert f'mdpo-{command_name}' in valid_command_names
