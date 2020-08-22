#!/usr/bin/env python

import argparse
import io
import re
import sys

try:
    from itertools import izip
except ImportError:
    izip = zip

import md2po


def parse_keyvalue_argument(text):
    return {x: y for x, y in izip(*[iter(re.split(':|,', text))]*2)}


def parse_list_argument(text, splitter=','):
    return tuple(filter(None, text.split(splitter)))


def parse_options():
    """
    Define and parse `optparse` options for command-line usage.
    """

    parser = argparse.ArgumentParser(description=md2po.__description__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + md2po.__version__)
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('glob_or_content', metavar='GLOB_OR_CONTENT',
                        nargs='?', default=sys.stdin,
                        help='Glob to markdown input files or markdown' +
                             ' content as a string.')
    parser.add_argument('-i', '--ignore', dest='ignore', default=None,
                        help='List of filepaths to ignore if' +
                             ' \'glob_or_content\' argument is a glob,' +
                             ' as a list of comma separated values.',
                        metavar='PATH_1,PATH_2...')
    parser.add_argument('-f', '--filepath', dest='po_filepath', default=None,
                        help='Merge new msgids in the po file indicated' +
                             ' at this parameter (if \'--save\' argument' +
                             ' is passed) or use the msgids of the file' +
                             ' as reference for' +
                             ' \'--mark-not-found-as-obsolete\' parameter.',
                        metavar='OUTPUT_FILE')
    parser.add_argument('-s', '--save', dest='save', action='store_true',
                        help='Save new found msgids to the po file' +
                             ' indicated as parameter \'--filepath\'.')
    parser.add_argument('-m', '--markuptext', dest='markuptext',
                        action='store_true',
                        help='Include markdown markup characters in' +
                             ' extracted msgids for **bold text**,' +
                             ' *italic text*, `inline code` and `[links]`.')
    parser.add_argument('-w', '--wrapwidth', dest='wrapwidth',
                        help='Wrap width for po file indicated at' +
                             ' \'--filepath\' parameter. Only useful when' +
                             ' the \'-w\' option was passed to xgettext.',
                        metavar='N', type=int)
    parser.add_argument('-o', '--mark-not-found-as-obsolete',
                        dest='mark_not_found_as_absolete',
                        action='store_true',
                        help='Mark new found msgids not present in the ' +
                             ' pofile passed at \'--filepath\' parameter' +
                             ' as obsolete translations.')
    parser.add_argument('-rc', '--replacement-chars', dest='replacement_chars',
                        default=None,
                        metavar='CHAR_A:CHAR_B,CHAR_C:CHAR_D...',
                        help='Map of characters to replace in output msgids.')
    parser.add_argument('-fm', '--forbidden-msgids', dest='forbidden_msgids',
                        default=None,
                        metavar='CHAR_A,CHAR_B,CHAR_C...',
                        help='List of comma separated values to ignore as' +
                             ' msgids if are found.')
    parser.add_argument('-bs', '--bold-string', dest='bold_string',
                        default=None,
                        help='String that represents the markup ' +
                             ' character/s at start and the end of a chunk' +
                             ' of bold text.',
                        metavar='CHAR/S', type=str)
    parser.add_argument('-is', '--italic-string', dest='italic_string',
                        default=None,
                        help='String that represents the markup ' +
                             ' character/s at the beginning and the end' +
                             ' of an italic text.',
                        metavar='CHAR/S', type=str)
    parser.add_argument('-cs', '--code-string', dest='code_string',
                        default=None,
                        help='String that represents the markup ' +
                             ' character/s at the beginning and the end' +
                             ' of an inline piece of code.',
                        metavar='CHAR/S', type=str)
    parser.add_argument('-lss', '--link-start-string',
                        dest='link_start_string', default=None,
                        help='String that represents the markup ' +
                             ' character/s at the beggining of a link.',
                        metavar='CHAR/S', type=str)
    parser.add_argument('-les', '--link-end-string', dest='link_end_string',
                        default=None,
                        help='String that represents the markup ' +
                             ' character/s at the beginning and the end' +
                             ' of a link.',
                        metavar='CHAR/S', type=str)
    opts = parser.parse_args()

    if isinstance(opts.glob_or_content, io.TextIOWrapper):
        opts.glob_or_content = opts.glob_or_content.read().strip('\n')
    if opts.ignore:
        opts.ignore = parse_list_argument(opts.ignore)
    if opts.replacement_chars:
        opts.replacement_chars = parse_keyvalue_argument(
            opts.replacement_chars)
    if opts.forbidden_msgids:
        opts.forbidden_msgids = parse_list_argument(opts.forbidden_msgids)

    return opts


def run():
    options = parse_options()

    kwargs = dict(
        po_filepath=options.po_filepath,
        ignore=options.ignore,
        save=options.save,
        plaintext=not options.markuptext,
        mark_not_found_as_absolete=options.mark_not_found_as_absolete,
        replacement_chars=options.replacement_chars,
        forbidden_msgids=options.forbidden_msgids)
    if isinstance(options.wrapwidth, int):
        kwargs['wrapwidth'] = options.wrapwidth

    markup_parameters = ['bold_string', 'italic_string', 'code_string',
                         'link_start_string', 'link_end_string']
    for param in markup_parameters:
        value = getattr(options, param)
        if value is not None:
            kwargs[param] = value

    pofile = md2po.markdown_to_pofile(options.glob_or_content, **kwargs)

    if not options.quiet:
        sys.stdout.write('%s\n' % pofile.__unicode__())

    return 0


if __name__ == '__main__':
    sys.exit(run())
