import pytest

from mdpo.cli import parse_command_aliases_cli_arguments


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
def test_parse_command_aliases_cli_arguments(
    command_aliases,
    expected_response,
    expected_stderr,
    capsys,
):
    if expected_stderr:
        with pytest.raises(SystemExit):
            parse_command_aliases_cli_arguments(command_aliases)
        out, err = capsys.readouterr()
        assert expected_stderr in err
    else:
        assert parse_command_aliases_cli_arguments(
            command_aliases,
        ) == expected_response
