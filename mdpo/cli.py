"""mdpo command line interface utilities."""

import argparse
import sys

from mdpo import __version__
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.text import parse_escaped_pairs


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


def add_common_cli_first_arguments(parser, quiet=True):
    """Add common mdpo arguments to an argument parser at the beginning.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
        quiet (bool): Include the argument ``-q/--quiet``.
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
    if quiet:
        parser.add_argument(
            '-q', '--quiet', action='store_true',
            help='Do not print output to STDOUT.',
        )


def add_common_cli_latest_arguments(parser):
    """Add common mdpo arguments to an argument parser at the end.

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


def add_extensions_argument(parser):
    """Add the ``-x/--extension`` argument to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '-x', '--extension', '--ext', dest='extensions', action='append',
        default=None,
        help='md4c extension used to parse markdown content formatted as'
             ' pymd4c extension keyword arguments. This argument can be passed'
             ' multiple times. If is not passed, next extensions are used:'
             f' {", ".join(DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS)}.'
             ' You can see all available at'
             ' https://github.com/dominickpastore/pymd4c#parser-option-flags',
        metavar='EXTENSION',
    )


def add_debug_option(parser):
    """Add the ``-D/--debug`` option to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '-D', '--debug', dest='debug', action='store_true',
        help='Print useful messages in the parsing process showing the'
             ' contents of all Markdown elements.',
    )


def add_nolocation_option(parser):
    """Add the ``--no-location/--nolocation`` option to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '--no-location', '--nolocation', dest='location', action='store_false',
        help="Do not write '#: filename:line' lines. Note that using this"
             ' option makes it harder for technically skilled translators to'
             " understand each message's context. Same as 'xgettext "
             "--no-location'.",
    )


def add_encoding_arguments(parser, po_encoding_help=None):
    """Add ``--po-encoding`` ``--md_encoding`` arguments to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
        po_encoding_help (str): Help text for the ``--po-encoding`` argument.
    """
    parser.add_argument(
        '--md-encoding', dest='md_encoding', default='utf-8',
        help='Markdown content encoding.', metavar='ENCODING',
    )

    po_encoding_help = (
        'PO files encoding. If you need different encodings for each'
        ' file, you must define them in the Content-Type" field of each'
        ' PO file metadata, in the form \'Content-Type: text/plain;'
        ' charset=<ENCODING>\\n\'.'
    ) if po_encoding_help is None else po_encoding_help
    parser.add_argument(
        '--po-encoding', dest='po_encoding', default=None, metavar='ENCODING',
        help=po_encoding_help,
    )


def add_pre_commit_option(parser):
    """Add the ``--pre-commit`` option to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '--pre-commit', dest='check_saved_files_changed', action='store_true',
        help='Run in pre-commit mode, which returns code 1 at exit when a file'
             ' has been changed or previously didn\'t exist.',
    )
