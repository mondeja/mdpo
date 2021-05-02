import pytest

from mdpo.cli import (
    parse_command_aliases_cli_argument,
    parse_escaped_pair_cli_argument,
)


@pytest.mark.parametrize(
    ('text', 'expected_key', 'expected_value', 'expected_error'),
    (
        ('foo:bar', 'foo', 'bar', None),
        ('foo:Bar:', 'foo', 'Bar:', None),
        ('foo:Bar\\:', 'foo', 'Bar\\:', None),
        (r'foo\\:Bar:baz', 'foo:Bar', 'baz', None),
        (r'foo\\:Bar:baz\\', 'foo:Bar', r'baz\\', None),
        # : at the beginning means escaped
        (r':foo\\:Bar:baz\\', ':foo:Bar', r'baz\\', None),
        ('foo', None, None, ValueError),
        (':', None, None, ValueError),
    ),
)
def test_parse_escaped_pair_cli_argument(
    text,
    expected_key,
    expected_value,
    expected_error,
):
    if expected_error:
        with pytest.raises(expected_error):
            parse_escaped_pair_cli_argument(text)
    else:
        key, value = parse_escaped_pair_cli_argument(text)
        assert key == expected_key
        assert value == expected_value


@pytest.mark.parametrize(
    ('command_aliases', 'expected_response', 'expected_stderr'),
    (
        pytest.param(
            ['foo:bar'],
            {'foo': 'bar'},
            None,
            id='foo:bar-{"foo": "bar"}',
        ),
        pytest.param(
            ['foo:bar', r'baz\\::qux'],
            {'foo': 'bar', 'baz:': 'qux'},
            None,
            id=r'foo:bar,baz\\::qux-{"foo": "bar", "baz:": "qux"}',
        ),
        pytest.param(
            ['foobar'],
            None,
            (
                "The value 'foobar' passed to argument --command-alias"
                " can't be parsed."
            ),
            id='foobar-error: unparsed alias resolution',
        ),
        pytest.param(
            ['foo:bar', 'foo:baz'],
            None,
            (
                "Multiple resolutions for 'foo' alias passed to"
                ' --command-alias arguments.'
            ),
            id='foo:bar,foo:baz-error: multiple resolutions for alias',
        ),
    ),
)
def test_parse_command_aliases_cli_argument(
    command_aliases,
    expected_response,
    expected_stderr,
    capsys,
):
    if expected_stderr:
        with pytest.raises(SystemExit):
            parse_command_aliases_cli_argument(command_aliases)
        out, err = capsys.readouterr()
        assert expected_stderr in err
    else:
        assert parse_command_aliases_cli_argument(
            command_aliases,
        ) == expected_response
