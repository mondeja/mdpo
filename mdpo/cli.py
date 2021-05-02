"""mdpo command line interface utilities."""

import argparse
import sys

from mdpo import __version__
from mdpo.text import parse_escaped_pairs


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


def parse_escaped_pairs_cli_argument(
    pairs,
    value_error_message,
    key_error_message,
):
    """Parses a key argument made by key-value pairs.

    If an error happens, shows an appropiate message and exists with code 1.

    Args:
        pairs (list): List of key-value pairs.
        value_error_message (str): Error message schema shown when a pair
            can't be parsed.
        key_error_message (str): Error message schema shown when a key is
            repeated.

    Returns:
        dict: Parsed key-value pairs.
    """
    try:
        return parse_escaped_pairs(pairs)
    except ValueError as err:
        sys.stderr.write(value_error_message.format(err.args[0]))
        sys.exit(1)
    except KeyError as err:
        sys.stderr.write(key_error_message.format(err.args[0]))
        sys.exit(1)


def parse_command_aliases_cli_arguments(command_aliases):
    """Parse ``--command-alias`` argument values passed to CLIs.

    If a value can't be passed or a custom command is duplicated, writes an
    appropiate error message to STDERR and exits with code 1.

    Args:
        command_aliases (list): Values taken by ``--command-alias`` arguments.

    Returns:
        dict: Command aliases mapping ni the format accepted by the API.
    """
    return parse_escaped_pairs_cli_argument(
        command_aliases,
        (
            "The value '{}' passed to argument --command-alias"
            " can't be parsed. Please, separate the pair "
            "'<custom-command:mdpo-command>' with a ':' character.\n"
        ),
        (
            "Multiple resolutions for '{}' alias passed to"
            ' --command-alias arguments.\n'
        ),
    )


def parse_metadata_cli_arguments(metadata):
    """Parse ``--metadata`` argument values passed to CLIs.

    If a value can't be passed or a metadata key is duplicated, writes an
    appropiate error message to STDERR and exits with code 1.

    Args:
        metadata (list): Values taken by ``--metadata`` arguments.

    Returns:
        dict: Metadata mapping ni the format accepted by the API.
    """
    return parse_escaped_pairs_cli_argument(
        metadata,
        (
            "The value '{}' passed to argument --metadata"
            " can't be parsed. Please, separate the pair "
            "'<key:value>' with a ':' character.\n"
        ),
        (
            "Repeated key '{}' passed to --metadata arguments.\n"
        ),
    )


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
