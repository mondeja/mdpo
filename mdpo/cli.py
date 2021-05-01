"""mdpo command line interface utilities."""

import argparse
import re
import sys

from mdpo import __version__


ESCAPED_PAIR_RE = re.compile(r'([^\\]:)')  # ':' is the separator


def parse_list_cli_argument(value, splitter=','):
    """Converts values in a string separated by characters into a tuple.

    This function is needed by mdpo command line interfaces to convert
    some arguments values separated by commas into iterables.

    Args:
        value (str): String to be converted to list separating it by
            ``splitter`` argument value.
        splitter (str): Separator used for separate the ``value`` argument.

    Returns:
        tuple: Strings separated.
    """
    return tuple(filter(None, value.split(splitter)))


def parse_escaped_pair_cli_argument(value):
    r"""Escapes a pair value separated by the character ':'.

    The separator can be escaped using the character '\'.

    Args:
        value (str): String to be converted to a pair key-value.

    Raises:
        ValueError: The value doesn't contains an unescaped separator.

    Returns:
        tuple: Parsed key-value pair.
    """
    splits = re.split(ESCAPED_PAIR_RE, value)
    if len(splits) == 1:
        raise ValueError()
    return (splits[0] + splits[1][0], splits[2])


def parse_command_aliases_cli_argument(command_aliases):
    """Parse ``--command-alias`` argument values passed to CLIs.

    If a value can't be passed or a custom command is duplicated, writes an
    appropiate error message to STDERR and exits with code 1.

    Args:
        command_aliases (list): Values taken by ``--command-alias`` arguments.

    Returns:
        dict: Command aliases mapping ni the format accepted by the API.
    """
    response = {}
    for alias_pair in command_aliases:
        try:
            custom_command, mdpo_command = parse_escaped_pair_cli_argument(
                alias_pair,
            )
        except ValueError:
            sys.stderr.write(
                f"The value '{alias_pair}' passed to argument --command-alias"
                " can't be parsed. Please, separate the pair "
                "'<custom-command:mdpo-command>' with a ':' character.\n",
            )
            sys.exit(1)

        if custom_command not in response:
            response[custom_command] = mdpo_command
        else:
            sys.stderr.write(
                f"Multiple resolutions for '{custom_command}' passed to"
                ' --command-alias arguments.\n',
            )
            sys.exit(1)
    return response


def add_common_cli_first_arguments(parser):
    """Adds common mdpo arguments to an argument parser at the beginning.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '-h', '--help', action='help',
        help='Show this help message and exit.',
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version=f'%(prog)s {__version__}',
        help='Show program version number and exit.',
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Do not print output to STDOUT.',
    )


def add_common_cli_latest_arguments(parser):
    """Adds common mdpo arguments to an argument parser at the end.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '--command-alias', dest='command_aliases', default=[], action='append',
        metavar='CUSTOM-COMMAND:MDPO-COMMAND',
        help='Aliases to use custom mdpo command names in comments. This'
             ' argument can be passed multiple times in the form'
             " '<custom-command>:<mdpo-command>'. The 'mdpo-' prefix in"
             ' command names resolution is optional. For example, if you want'
             " to use '<!-- mdpo-on -->' instead of '<!-- mdpo-enable -->',"
             ' you can pass either \'--command-alias "mdpo-on:mdpo-enable"\''
             ' or \'--command-alias "mdpo-on:enable"\' arguments.',
    )
