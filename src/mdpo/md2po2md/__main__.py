#!/usr/bin/env python

"""md2po2md command line interface.

See :ref:`md2po2md CLI<cli:md2po2md>`.
"""

import argparse
import itertools
import sys

from mdpo.cli import (
    SPHINX_IS_RUNNING,
    add_check_option,
    add_command_alias_argument,
    add_common_cli_first_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_extensions_argument,
    add_nolocation_option,
    add_wrapwidth_argument,
    cli_codespan,
    parse_command_aliases_cli_arguments,
)
from mdpo.io import environ
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
        '-l', '--lang', dest='langs', default=[], nargs='*',
        action='append',
        help='Language codes used to create the output directories.'
             ' This argument can be passed multiple times. Also, all'
             ' languages can be defined after this argument with'
             f" {cli_codespan('-l es_ES fr_FR de_DE')}.",
        metavar='LANG', required=True,
    )

    output_paths_schema_help = '' if SPHINX_IS_RUNNING else (
        ' For example, for the schema \'locale/{lang}\', the languages'
        ' \'es\' and \'fr\' and a \'README.md\' as input, the next files'
        ' will be written: \'locale/es/README.po\', \'locale/es/README.md\','
        ' \'locale/fr/README.po\' and \'locale/fr/README.md\'.'
        ' Note that you can omit \'{basename}\', specifying a'
        ' directory for each language with \'locale/{lang}\' for this'
        ' example.'
    )
    parser.add_argument(
        '-o', '--output', dest='output_paths_schema', required=True, type=str,
        help='Path schema for outputs, built using placeholders. There is a'
             ' mandatory placeholder for languages: {lang};and one optional'
             f' for output basename: {{basename}}.{output_paths_schema_help}'
             ' Unexistent directories and files will be created, so you do not'
             ' have to prepare the output directories before the execution.',
        metavar='PATH_SCHEMA',
    )
    add_nolocation_option(parser)
    add_extensions_argument(parser)
    add_command_alias_argument(parser)
    add_wrapwidth_argument(
        parser,
        markup='po',
        markup_prefix=True,
        short=False,
        help_to_render='PO files',
    )
    add_wrapwidth_argument(
        parser, markup='md', markup_prefix=True, short=False, default='80',
    )
    add_encoding_arguments(parser)
    add_debug_option(parser)
    add_check_option(parser)
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
    if not input_paths_glob:
        sys.stderr.write('Files or content to translate not specified\n')
        sys.exit(1)
    opts.input_paths_glob = input_paths_glob

    opts.langs = set(itertools.chain(*opts.langs))  # flatten

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

        kwargs = {
            'extensions': opts.extensions,
            'command_aliases': opts.command_aliases,
            'debug': opts.debug,
            'location': opts.location,
            'po_wrapwidth': opts.po_wrapwidth,
            'md_wrapwidth': opts.md_wrapwidth,
            'po_encoding': opts.po_encoding,
            'md_encoding': opts.md_encoding,
            '_check_saved_files_changed': opts.check_saved_files_changed,
        }

        _saved_files_changed = markdown_to_pofile_to_markdown(
            opts.langs,
            opts.input_paths_glob,
            opts.output_paths_schema,
            **kwargs,
        )
        if opts.check_saved_files_changed and _saved_files_changed:
            exitcode = 1
    return exitcode


def main():
    raise SystemExit(run(args=sys.argv[1:]))  # pragma: no cover


if __name__ == '__main__':
    main()
