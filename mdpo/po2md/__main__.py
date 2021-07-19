#!/usr/bin/env python

"""po2md command line interface."""

import argparse
import itertools
import sys

from mdpo.cli import (
    add_common_cli_first_arguments,
    add_common_cli_latest_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_pre_commit_option,
    parse_command_aliases_cli_arguments,
)
from mdpo.context import environ
from mdpo.po2md import Po2Md


DESCRIPTION = (
    'Markdown files translator using pofiles as reference.\n\n'
    'This implementation reproduces the same valid Markdown output, given the'
    " provided AST, with replaced translations, but doesn't rebuilds the same"
    ' input format as Markdown is just a subset of HTML.'
)


def build_parser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'filepath_or_content', metavar='FILEPATH_OR_CONTENT',
        nargs='*',
        help='Markdown filepath or content to translate.'
             ' If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-p', '--po-files', '--pofiles', metavar='POFILES', action='append',
        nargs='*', dest='pofiles',
        help='Glob matching a set of PO files from where to extract references'
             ' to make the replacements translating strings. This argument'
             ' can be passed multiple times.',
    )
    parser.add_argument(
        '-i', '--ignore', dest='ignore', default=[], action='append',
        help='Filepath to ignore when \'--pofiles\' argument value is a glob.'
             ' This argument can be passed multiple times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', default=None,
        help='Saves the output content in a file whose path is'
             ' specified at this parameter.', metavar='PATH',
    )
    parser.add_argument(
        '-w', '--wrapwidth', dest='wrapwidth', default='80', type=str,
        help='Maximum width rendering the Markdown output, when possible. You'
             ' can use the values \'0\' and \'inf\' for infinite width.',
        metavar='N/inf',
    )
    add_encoding_arguments(parser)
    add_common_cli_latest_arguments(parser)
    add_debug_option(parser)
    add_pre_commit_option(parser)
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
    opts.filepath_or_content = filepath_or_content

    opts.command_aliases = parse_command_aliases_cli_arguments(
        opts.command_aliases,
    )

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
            debug=opts.debug,
            _check_saved_files_changed=opts.check_saved_files_changed,
        )

        output = po2md.translate(
            opts.filepath_or_content,
            save=opts.save,
            md_encoding=opts.md_encoding,
        )

        if not opts.quiet and not opts.save:
            sys.stdout.write(output + '\n')

        # pre-commit mode
        if (  # pragma: no cover
            opts.check_saved_files_changed and po2md._saved_files_changed
        ):
            return (output, 1)

    return (output, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
