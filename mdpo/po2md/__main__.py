#!/usr/bin/env python

"""po2md command line interface.

See :ref:`po2md CLI<cli:po2md>`.
"""

import argparse
import itertools
import sys

from mdpo.cli import (
    add_check_option,
    add_command_alias_argument,
    add_common_cli_first_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_event_argument,
    add_wrapwidth_argument,
    cli_codespan,
    parse_command_aliases_cli_arguments,
    parse_event_argument,
)
from mdpo.io import environ
from mdpo.po2md import Po2Md


DESCRIPTION = (
    'Markdown file translator using PO files as reference.\n\n'
    'This implementation reproduces the same valid Markdown output, given the'
    ' provided content, with translations replaced, but does not produces the'
    ' same input format.'
)


def build_parser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser._positionals.title = 'positional argument'
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'filepath_or_content', metavar='FILEPATH_OR_CONTENT',
        nargs='*',
        help='Markdown filepath or content to translate.'
             ' If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-p', '--po-files', '--pofiles', metavar='POFILES', action='append',
        nargs='*', dest='pofiles', required=True,
        help='Glob matching a set of PO files from where to extract references'
             ' to make the replacements translating strings. This argument'
             ' can be passed multiple times.',
    )
    parser.add_argument(
        '-i', '--ignore', dest='ignore', default=[], action='append',
        help=f'Filepath to ignore when {cli_codespan("--pofiles")} argument'
             ' value is a glob. This argument can be passed multiple times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', default=None,
        help='Saves the output content in a file whose path is specified at'
             ' this parameter.', metavar='PATH',
    )
    add_wrapwidth_argument(parser, markup='md', default='80')
    add_encoding_arguments(parser)
    add_command_alias_argument(parser)
    add_event_argument(parser)
    add_debug_option(parser)
    add_check_option(parser)
    return parser


def parse_options(args):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(1)
    opts = parser.parse_args(args)

    filepath_or_content = ''
    if not sys.stdin.isatty():
        filepath_or_content += sys.stdin.read().strip('\n')
    if (
        isinstance(opts.filepath_or_content, list)
        and opts.filepath_or_content
    ):
        filepath_or_content += opts.filepath_or_content[0]
    if not filepath_or_content:
        sys.stderr.write('Files or content to translate not specified\n')
        sys.exit(1)
    opts.filepath_or_content = filepath_or_content

    opts.command_aliases = parse_command_aliases_cli_arguments(
        opts.command_aliases,
    )
    opts.events = parse_event_argument(opts.events)

    opts.pofiles = set(itertools.chain(*opts.pofiles))  # flatten

    return opts


def run(args=[]):
    with environ(_MDPO_RUNNING='true'):
        opts = parse_options(args)

        po2md = Po2Md(
            opts.pofiles,
            ignore=opts.ignore,
            po_encoding=opts.po_encoding,
            command_aliases=opts.command_aliases,
            wrapwidth=opts.wrapwidth,
            events=opts.events,
            debug=opts.debug,
            _check_saved_files_changed=opts.check_saved_files_changed,
        )

        output = po2md.translate(
            opts.filepath_or_content,
            save=opts.save,
            md_encoding=opts.md_encoding,
        )

        if not opts.quiet and not opts.save:
            sys.stdout.write(f'{output}\n')

        # pre-commit mode
        if opts.check_saved_files_changed and po2md._saved_files_changed:
            return (output, 1)

    return (output, 0)


def main():
    raise SystemExit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
