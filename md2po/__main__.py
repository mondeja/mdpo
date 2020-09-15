#!/usr/bin/env python

import argparse
import io
import sys


try:
    from itertools import izip
except ImportError:
    izip = zip

import md2po


def parse_list_argument(text, splitter=','):
    return tuple(filter(None, text.split(splitter)))


def build_parser():
    parser = argparse.ArgumentParser(description=md2po.__description__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + md2po.__version__,
                        help='Show program version number and exit.')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Don\'t print output to STDOUT.')
    parser.add_argument('glob_or_content', metavar='GLOB_OR_CONTENT',
                        nargs='?', default=sys.stdin,
                        help='Glob to markdown input files or markdown'
                             ' content as a string. If not provided,'
                             ' will be read from STDIN.')
    parser.add_argument('-i', '--ignore', dest='ignore', default=None,
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
                        default=md2po.DEFAULT_MD4C_FLAGS, dest='flags',
                        help='md4c extensions used to parse markdown'
                             ' content, separated by ``|`` or ``+``'
                             '  characters. You can see all available at http'
                             's://github.com/mity/md4c#markdown-extensions')
    parser.add_argument('-fm', '--forbidden-msgids', dest='forbidden_msgids',
                        default=None,
                        metavar='CHAR_A,CHAR_B,CHAR_C...',
                        help='List of comma separated values to ignore as'
                             ' msgids if are found.')
    parser.add_argument('-e', '--encoding', dest='encoding', default=None,
                        help='Resulting pofile encoding (autodetected by'
                             ' default).')
    return parser


def parse_options(args):
    parser = build_parser()
    opts = parser.parse_args(args)

    if isinstance(opts.glob_or_content, io.TextIOWrapper):
        opts.glob_or_content = opts.glob_or_content.read().strip('\n')
    if opts.ignore:
        opts.ignore = parse_list_argument(opts.ignore)
    if opts.forbidden_msgids:
        opts.forbidden_msgids = parse_list_argument(opts.forbidden_msgids)

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
        forbidden_msgids=opts.forbidden_msgids,
        encoding=opts.encoding)
    if isinstance(opts.wrapwidth, int):
        kwargs['wrapwidth'] = opts.wrapwidth

    pofile = md2po.markdown_to_pofile(opts.glob_or_content, **kwargs)

    if not opts.quiet:
        sys.stdout.write('%s\n' % pofile.__unicode__())

    return (pofile, 0)


if __name__ == '__main__':
    sys.exit(run(args=sys.argv[1:])[1])
