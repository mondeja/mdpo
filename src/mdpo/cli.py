"""mdpo command line interface utilities."""

import argparse
import sys

from importlib_metadata_argparse_version import ImportlibMetadataVersionAction

from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.text import and_join, parse_escaped_pairs


SPHINX_IS_RUNNING = 'sphinx' in sys.modules
OPEN_QUOTE_CHAR = '”' if SPHINX_IS_RUNNING else '"'
CLOSE_QUOTE_CHAR = '”' if SPHINX_IS_RUNNING else '"'


def cli_codespan(value, cli=True, sphinx=True):
    """Command line codespan wrapper.

    This is a compatibility function to make CLI codespans looks good in
    sphinx-argparse-cli documentation and using ``--help`` option in CLI
    itself. sphinx-argparse-cli expects the usage of double backticks for
    codespans, but that format is ugly in CLI.

    Args:
        value (str): Value to wrap.
        cli (bool): Wrap when used from command line.
        sphinx (bool): Wrap when used from Sphinx.
    """
    if SPHINX_IS_RUNNING:
        return f'``{value}``' if sphinx else value
    else:
        return f'\'{value}\'' if cli else value


def parse_escaped_pairs_cli_argument(
    pairs,
    value_error_message,
    key_error_message,
):
    """Parse a key argument made by key-value pairs.

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
        '-v', '--version', action=ImportlibMetadataVersionAction,
        version='%(prog)s %(version)s',
        importlib_metadata_version_from='mdpo',
        help='Show program version number and exit.',
    )
    if quiet:
        parser.add_argument(
            '-q', '--quiet', action='store_true',
            help='Do not print output to STDOUT.',
        )


def add_command_alias_argument(parser):
    """Add the ``--command-alias`` argument to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    mdpo_on_mdpo_enable = cli_codespan(
        f'--command-alias {OPEN_QUOTE_CHAR}mdpo-on:mdpo-enable'
        f'{CLOSE_QUOTE_CHAR}',
    )
    mdpo_on_enable = cli_codespan(
        f'--command-alias {OPEN_QUOTE_CHAR}mdpo-on:enable'
        f'{CLOSE_QUOTE_CHAR}',
    )
    command_alias_help_example = (
        ' For example, if you want to use "<!-- mdpo-on -->" instead of'
        f' "<!-- mdpo-enable -->", you can pass either {mdpo_on_mdpo_enable}'
        f' or {mdpo_on_enable} arguments.'
    )
    parser.add_argument(
        '--command-alias', dest='command_aliases', default=[], action='append',
        metavar='CUSTOM-COMMAND:MDPO-COMMAND',
        help='Aliases to use custom mdpo command names in comments. This'
             ' argument can be passed multiple times in the form'
             ' "<custom-command>:<mdpo-command>". The \'mdpo-\' prefix in'
             ' command names resolution is optional.'
             f'{command_alias_help_example}',
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
             ' multiple times. If it is not passed, next extensions are used:'
             f' {and_join(DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS)}.'
             ' You can see all available at'
             ' https://pymd4c.dcpx.org/api.html#parser-option-flags',
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
        help='Do not write \'#: filename:line\' lines. Note that using this'
             ' option makes it harder for technically skilled translators to'
             ' understand the context of each message. Same as'
             f' {cli_codespan("gettext --no-location")}.',
    )


def add_encoding_arguments(
    parser,
    po_encoding_help=None,
    markup_encoding='md',
):
    """Add ``--po-encoding`` ``--md-encoding`` arguments to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
        po_encoding_help (str): Help text for the ``--po-encoding`` argument.
        markup_encoding (str): Type of markup encoding, can be ``"md"`` or
            ``"html"``.
    """
    parser.add_argument(
        f'--{markup_encoding}-encoding',
        dest=f'{markup_encoding}_encoding',
        default='utf-8',
        help=f'{"Markdown" if markup_encoding == "md" else "HTML"}'
             ' content encoding.',
        metavar='ENCODING',
    )

    po_encoding_help = (
        'PO files encoding. If you need different encodings for each'
        ' file, you must define them in the "Content-Type" field of each'
        ' PO file metadata, in the form \'Content-Type: text/plain;'
        ' charset=<ENCODING>\'.'
    ) if po_encoding_help is None else po_encoding_help
    parser.add_argument(
        '--po-encoding', dest='po_encoding', default=None, metavar='ENCODING',
        help=po_encoding_help,
    )


def add_wrapwidth_argument(
    parser,
    markup='po',
    markup_prefix=False,
    short=True,
    default='78',
    help_to_render=None,
):
    """Add a ``--wrapwidth`` argument to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
        markup (str): For which type of files the argument will affect. Either
            ``"md"`` for Markdown or ``"po"`` for PO files.
        markup_prefix (bool): Add the ``markup`` prefix in the argument using
            the format ``--<markup>-wrapwidth``.
        short (bool): Add the short version of the argument (``-w``).
        default (str): Default value.
        help_to_render (str): String used to indicate the content that will be
            wrapped according to the argument.
    """
    args = [f'--{markup}-wrapwidth' if markup_prefix else '--wrapwidth']
    if short:
        args.append('-w')

    kwargs = {
        'metavar': 'N/inf',
        'type': str,
        'default': default,
    }
    if help_to_render is not None:
        to_render = help_to_render
    elif markup == 'po':
        to_render = (
            'the PO file indicated at parameter'
            f' {cli_codespan("--po-filepath")}'
        )
    else:
        to_render = 'the Markdown output, when possible'
    kwargs['help'] = (
        f'Maximum width rendering {to_render}. If negative, \'0\' or \'inf\','
        ' the content will not be wrapped.'
    )
    parser.add_argument(*args, **kwargs)


def add_check_option(parser):
    """Add the ``--check`` option to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '--check', dest='check_saved_files_changed', action='store_true',
        help='Run in check mode, which returns code 1 at exit when a file'
             ' has been changed or previously did not exist.',
    )


def add_event_argument(parser):
    """Add the ``--event`` optional argument to an argument parser.

    Args:
        parser (:py:class:`argparse.ArgumentParser`): Arguments parser to
            extend.
    """
    parser.add_argument(
        '-e', '--event', dest='events', default=[], action='append',
        metavar='event_name: path/to/file.py::function_name',
        help='Custom events executed during the parser. They are used for'
             ' customize the output. See the documentation for available'
             ' event names. This argument can be passed multiple times.',
    )


def parse_event_argument(value):
    """Parse ``--event`` CLI argument values.

    Args:
        value (list): Event names and function paths in the form
            ``event_name: path/to/file.py::func``.

    Returns:
        dict: Mapping of event names and `file::function` paths.
    """
    events = {}
    for event_name_filefunc in value:
        event_name, filefunc = event_name_filefunc.split(':', maxsplit=1)
        events[event_name.strip()] = filefunc.strip()
    return events
