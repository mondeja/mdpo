"""mdpo command line interface utilities."""

import argparse

from mdpo import __version__


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


def add_common_cli_arguments(parser):
    """Adds common mdpo arguments to an argument parser.

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
