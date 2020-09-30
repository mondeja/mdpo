#!/usr/bin/env python

"""md2po command line interface."""

import argparse
import io
import sys
try:
    from itertools import izip
except ImportError:
    izip = zip

from mdpo import __version__
from mdpo.cli import parse_list_argument
from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_FLAGS


DESCRIPTION = ('Utility like xgettext to extract Markdown content dumping it'
               ' inside .po files.')


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__,
                        help='Show program version number and exit.')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Don\'t print output to STDOUT.')
    parser.add_argument('glob_or_content', metavar='GLOB_OR_CONTENT',
                        nargs='?', default=sys.stdin,
                        help='Glob to markdown input files or markdown'
                             ' content as a string. If not provided,'
                             ' will be read from STDIN.')
    parser.add_argument('-i', '--ignore', dest='ignore', default=[],
                        help='List of filepaths to ignore if'
                             ' ``GLOB_OR_CONTENT`` argument is a glob,'
                             ' as a list of comma separated values.',
                        metavar='PATH_1,PATH_2...')
    parser.add_argument('-f', '--filepath', dest='po_filepath', default=None,
                        help='Merge new msgids in the po file indicated'
                             ' at this parameter (if ``--save`` argument'
                             ' is passed) or use the msgids of the file'
                             ' as reference for'
                             ' ``--mark-not-found-as-obsolete`` parameter.',
                        metavar='OUTPUT_FILE')
    parser.add_argument('-s', '--save', dest='save', action='store_true',
                        help='Save new found msgids to the po file'
                             ' indicated as parameter ``--filepath``.')
    parser.add_argument('-m', '--markuptext', dest='markuptext',
                        action='store_true',
                        help='Include markdown markup characters in'
                             ' extracted msgids for **bold text**,'
                             ' *italic text*, `inline code` and `[links]`.')
    parser.add_argument('-w', '--wrapwidth', dest='wrapwidth',
                        help='Wrap width for po file indicated at'
                             ' ``--filepath`` parameter. Only useful when'
                             ' the ``-w`` option was passed to xgettext.',
                        metavar='N', type=int)
    parser.add_argument('-o', '--mark-not-found-as-obsolete',
                        dest='mark_not_found_as_absolete',
                        action='store_true',
                        help='Mark new found msgids not present in the '
                             ' pofile passed at ``--filepath`` parameter'
                             ' as obsolete translations.')
    parser.add_argument('-F', '--flags',
                        default=DEFAULT_MD4C_FLAGS, dest='flags',
                        help='md4c extensions used to parse markdown'
                             ' content, separated by ``|`` or ``+``'
                             '  characters. You can see all available at http'
                             's://github.com/mity/md4c#markdown-extensions')
    parser.add_argument('-e', '--encoding', dest='encoding', default=None,
                        help='Resulting pofile encoding (autodetected by'
                             ' default).')
    parser.add_argument('-x', '--xheaders', dest='xheaders',
                        action='store_true',
                        help='Include mdpo specification x-headers.'
                             ' These only will be included if you pass the'
                             ' parameter ``--markuptext``.')
    return parser


def parse_options(args):
    parser = build_parser()
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        sys.exit(0)
    opts = parser.parse_args(args)

    if isinstance(opts.glob_or_content, io.TextIOWrapper):
        opts.glob_or_content = opts.glob_or_content.read().strip('\n')
    if opts.ignore:
        opts.ignore = parse_list_argument(opts.ignore)

    return opts


def run(args=[]):
    opts = parse_options(args)

    kwargs = dict(
        po_filepath=opts.po_filepath,
        ignore=opts.ignore,
        save=opts.save,
        plaintext=not opts.markuptext,
        mark_not_found_as_absolete=opts.mark_not_found_as_absolete,
        flags=opts.flags,
        encoding=opts.encoding,
        xheaders=opts.xheaders)
    if isinstance(opts.wrapwidth, int):
        kwargs['wrapwidth'] = opts.wrapwidth

    pofile = markdown_to_pofile(opts.glob_or_content, **kwargs)

    if not opts.quiet:
        sys.stdout.write('%s\n' % pofile.__unicode__())

    return (pofile, 0)


if __name__ == '__main__':
    sys.exit(run(args=sys.argv[1:])[1])
