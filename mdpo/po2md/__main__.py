#!/usr/bin/env python

"""po2md command line interface."""

import argparse
import sys

from mdpo import __version__
from mdpo.cli import parse_list_argument
from mdpo.po2md import pofile_to_markdown

DESCRIPTION = 'Markdown files translator using pofiles as reference.'


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__,
                        help='Show program version number and exit.')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Don\'t print output to STDOUT.')
    parser.add_argument('filepath_or_content', metavar='FILEPATH_OR_CONTENT',
                        help='Markdown filepath or content to translate.')
    parser.add_argument('-p', '--pofiles', metavar='POFILES',
                        help='Glob matching a set of pofiles from where to'
                             ' extract references to make the replacements'
                             ' translating strings.')
    parser.add_argument('-i', '--ignore', dest='ignore', default=[],
                        help='List of filepaths to ignore if ``POFILES``'
                             ' argument is a glob, as a list of comma'
                             ' separated values.',
                        metavar='PATH_1,PATH_2...')
    parser.add_argument('-s', '--save', dest='save', default=None,
                        help='Saves the output content in file whose path is'
                             ' specified at this parameter.', metavar='PATH')
    return parser


def parse_options(args):
    parser = build_parser()
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        sys.exit(0)
    opts = parser.parse_args(args)

    if not sys.stdin.isatty():
        opts.filepath_or_content = sys.stdin.read().strip('\n')
    if opts.ignore:
        opts.ignore = parse_list_argument(opts.ignore)

    return opts


def run(args=[]):
    opts = parse_options(args)

    output = pofile_to_markdown(
        opts.filepath_or_content, opts.pofiles,
        ignore=opts.ignore, save=opts.save)

    if not opts.quiet and not opts.save:
        sys.stdout.write('%s\n' % output)

    return (output, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])


if __name__ == '__main__':
    main()
