#!/usr/bin/env python

"""mdpo2html command line interface."""

import argparse
import itertools
import sys

from mdpo.cli import (
    add_common_cli_first_arguments,
    add_common_cli_latest_arguments,
    parse_command_aliases_cli_arguments,
)
from mdpo.context import environ
from mdpo.mdpo2html import markdown_pofile_to_html


DESCRIPTION = (
    'HTML-produced-from-Markdown files translator using PO files'
    ' as reference.'
)


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'filepath_or_content', metavar='FILEPATH_OR_CONTENT',
        nargs='*',
        help='HTML filepath or content to translate. If not provided, will be'
             ' read from STDIN.',
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
        help='Filepaths to ignore when \'--pofiles\' argument value is a glob.'
             ' This argument can be passed multiple times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', default=None,
        help='Saves the output content in file whose path is specified at this'
             ' parameter.', metavar='PATH',
    )
    parser.add_argument(
        '--html-encoding', dest='html_encoding', default='utf-8',
        help='Markdown content encoding.', metavar='<ENCODING>',
    )
    parser.add_argument(
        '--po-encoding', dest='po_encoding', default=None,
        help='PO files encoding. If you need different encodings for each'
             ' file, you must define it in the "Content-Type" field of each'
             ' PO file metadata, in the form "Content-Type: text/plain;'
             ' charset=<ENCODING>\\n".',
        metavar='<ENCODING>',
    )
    add_common_cli_latest_arguments(parser)
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

        output = markdown_pofile_to_html(
            opts.filepath_or_content, opts.pofiles,
            ignore=opts.ignore, save=opts.save,
            po_encoding=opts.po_encoding,
            html_encoding=opts.html_encoding,
            command_aliases=opts.command_aliases,
        )

        if not opts.quiet and not opts.save:
            sys.stdout.write(output + '\n')

    return (output, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
