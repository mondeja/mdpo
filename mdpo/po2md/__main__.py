#!/usr/bin/env python

"""po2md command line interface."""

import argparse
import itertools
import os
import sys

from mdpo.cli import (
    add_common_cli_first_arguments,
    add_common_cli_latest_arguments,
    parse_command_aliases_cli_arguments,
)
from mdpo.po2md import pofile_to_markdown


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
        help='Saves the output content in file whose path is'
             ' specified at this parameter.', metavar='PATH',
    )
    parser.add_argument(
        '-w', '--wrapwidth', dest='wrapwidth', default='80', type=str,
        help='Maximum width rendering the Markdown output, when possible. You'
             ' can use the values \'0\' and \'inf\' for infinite width.',
        metavar='N/inf',
    )
    parser.add_argument(
        '--md-encoding', dest='md_encoding', default='utf-8',
        help='Markdown content encoding.', metavar='<ENCODING>',
    )
    parser.add_argument(
        '--po-encoding', dest='po_encoding', default=None,
        help='PO files encoding. If you need different encodings for each'
             ' file, you must define them in the Content-Type" field of each'
             ' PO file metadata, in the form \'Content-Type: text/plain;'
             ' charset=<ENCODING>\\n\'.',
        metavar='<ENCODING>',
    )
    parser.add_argument(
        '-D', '--debug', dest='debug', action='store_true',
        help='Print useful messages in the parsing process showing the'
             ' contents of all Markdown elements.',
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
    prev_mdpo_running = os.environ.get('_MDPO_RUNNING')
    os.environ['_MDPO_RUNNING'] = 'true'

    try:
        opts = parse_options(args)

        output = pofile_to_markdown(
            opts.filepath_or_content, opts.pofiles,
            ignore=opts.ignore, save=opts.save,
            md_encoding=opts.md_encoding,
            po_encoding=opts.po_encoding,
            command_aliases=opts.command_aliases,
            wrapwidth=opts.wrapwidth,
            debug=opts.debug,
        )

        if not opts.quiet and not opts.save:
            sys.stdout.write(output + '\n')
    finally:
        if prev_mdpo_running is None:
            del os.environ['_MDPO_RUNNING']
        else:
            os.environ['_MDPO_RUNNING'] = prev_mdpo_running
    return (output, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
