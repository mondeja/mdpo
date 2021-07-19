#!/usr/bin/env python

"""md2po2md command line interface."""

import argparse
import sys

from mdpo.cli import (
    add_common_cli_first_arguments,
    add_common_cli_latest_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_extensions_argument,
    add_nolocation_option,
    add_pre_commit_option,
    parse_command_aliases_cli_arguments,
)
from mdpo.context import environ
from mdpo.md2po2md import markdown_to_pofile_to_markdown
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


DESCRIPTION = (
    'Translates Markdown files using PO files for a set of predefined language'
    ' codes creating multiple directories, one for each language.'
)


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
    add_common_cli_first_arguments(parser, quiet=False)
    parser.add_argument(
        'input_paths_glob', metavar='GLOB', nargs='*',
        help='Glob to markdown input files to translate.'
             ' If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-l', '--lang', dest='langs', default=[], action='append',
        help='Language codes used to create the output directories.'
             ' Can be passed multiple times.',
        metavar='LANG',
    )
    parser.add_argument(
        '-o', '--output', dest='output_paths_schema',
        required=True, type=str,
        help='Path schema for outputs, built using placeholders. There is a'
             ' mandatory placeholder for languages: \'{lang}\'; and one'
             ' optional for output basename: \'{basename}\'. For example,'
             ' for the schema \'locale/{lang}\', the languages \'es\' and'
             ' \'fr\' and a \'README.md\' as input, the next files will be'
             ' written: \'locale/es/README.po\', \'locale/es/README.md\','
             ' \'locale/fr/README.po\' and \'locale/fr/README.md\'.'
             ' Note that you can omit \'{basename}\', specifying a'
             ' directory for each language with \'locale/{lang}\' for this'
             ' example. Unexistent directories and files will be created, '
             ' so you don\'t have to prepare the output directories before'
             ' the execution.',
        metavar='PATH_SCHEMA',
    )
    add_nolocation_option(parser)
    add_extensions_argument(parser)
    add_common_cli_latest_arguments(parser)
    add_encoding_arguments(parser)
    add_debug_option(parser)
    add_pre_commit_option(parser)
    return parser


def parse_options(args=[]):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(1)
    opts, unknown = parser.parse_known_args(args)

    input_paths_glob = ''
    if not sys.stdin.isatty():
        input_paths_glob += sys.stdin.read().strip('\n')
    if isinstance(opts.input_paths_glob, list) and opts.input_paths_glob:
        input_paths_glob += opts.input_paths_glob[0]
    opts.input_paths_glob = input_paths_glob

    if opts.extensions is None:
        opts.extensions = DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS

    opts.command_aliases = parse_command_aliases_cli_arguments(
        opts.command_aliases,
    )

    return opts


def run(args=[]):
    exitcode = 0

    with environ(_MDPO_RUNNING='true'):
        opts = parse_options(args)

        kwargs = dict(
            extensions=opts.extensions,
            command_aliases=opts.command_aliases,
            debug=opts.debug,
            location=opts.location,
            po_encoding=opts.po_encoding,
            md_encoding=opts.md_encoding,
        )

        _saved_files_changed = markdown_to_pofile_to_markdown(
            opts.langs,
            opts.input_paths_glob,
            opts.output_paths_schema,
            _check_saved_files_changed=opts.check_saved_files_changed,
            **kwargs,
        )
        if (  # pragma: no cover
            opts.check_saved_files_changed and _saved_files_changed
        ):
            exitcode = 1
    return exitcode


def main():
    sys.exit(run(args=sys.argv[1:]))  # pragma: no cover


if __name__ == '__main__':
    main()
