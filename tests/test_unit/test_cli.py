import pytest
from mdpo.cli import parse_command_aliases_cli_arguments


@pytest.mark.parametrize(
    ('command_aliases', 'expected_result'),
    (
        pytest.param(
            ['foo:bar'],
            {'foo': 'bar'},
            id='foo:bar-{"foo": "bar"}',
        ),
        pytest.param(
            ['foo:bar', r'baz\\::qux'],
            {'foo': 'bar', 'baz:': 'qux'},
            id=r'foo:bar,baz\\::qux-{"foo": "bar", "baz:": "qux"}',
        ),
        pytest.param(
            ['foobar'],
            (
                "The value 'foobar' passed to argument --command-alias"
                " can't be parsed. Please, separate the pair"
                " '<custom-command:mdpo-command>' with a ':' character.\n"
            ),
            id='foobar-error: unparsed alias resolution',
        ),
        pytest.param(
            ['foo:bar', 'foo:baz'],
            (
                "Multiple resolutions for 'foo' alias passed to"
                ' --command-alias arguments.\n'
            ),
            id='foo:bar,foo:baz-error: multiple resolutions for alias',
        ),
    ),
)
def test_parse_command_aliases_cli_arguments(
    command_aliases,
    expected_result,
    capsys,
):

    if isinstance(expected_result, str):  # stderr expected
        with pytest.raises(SystemExit):
            parse_command_aliases_cli_arguments(command_aliases)
        stdout, stderr = capsys.readouterr()
        assert stderr == expected_result
        assert stdout == ''
    else:
        assert parse_command_aliases_cli_arguments(
            command_aliases,
        ) == expected_result
