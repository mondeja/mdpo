#!/usr/bin/env python

"""md2po command line interface."""

import argparse
import sys

from mdpo import __version__
from mdpo.cli import parse_list_argument
from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


DESCRIPTION = (
    'Utility like xgettext to extract Markdown content dumping it'
    ' inside pofiles.'
)


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s ' + __version__,
        help='Show program version number and exit.',
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Do not print output to STDOUT.',
    )
    parser.add_argument(
        'glob_or_content', metavar='GLOB_OR_CONTENT',
        nargs='*',
        help='Glob to markdown input files or markdown content as string.'
             ' If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-i', '--ignore', dest='ignore', default=[],
        help='Filepaths to ignore if ``GLOB_OR_CONTENT`` argument'
             ' is a glob, as a list of comma separated values.',
        metavar='PATH_1,PATH_2...',
    )
    parser.add_argument(
        '-po', '--po-filepath', dest='po_filepath',
        default=None,
        help='Merge new msgids in the po file indicated at this parameter (if'
             ' ``--save`` argument is passed) or use the msgids of the file as'
             ' reference for ``--mark-not-found-as-obsolete`` parameter.',
        metavar='OUTPUT_PO_FILEPATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', action='store_true',
        help='Save new found msgids to the po file'
             ' indicated as parameter ``--filepath``.',
    )
    parser.add_argument(
        '-mo', '--mo-filepath', dest='mo_filepath',
        default=None,
        help='The resulting pofile will be compiled to a mofile and saved in'
             ' the path specified at this parameter.',
        metavar='OUTPUT_MO_FILEPATH',
    )
    parser.add_argument(
        '-p', '--plaintext', dest='plaintext',
        action='store_true',
        help='Do not include markdown markup characters in extracted msgids'
             ' for **bold text**, *italic text*, `inline code` and'
             ' [link](target).',
    )
    parser.add_argument(
        '-w', '--wrapwidth', dest='wrapwidth',
        help='Wrap width for po file indicated at ``--filepath`` parameter.'
             ' Only useful when the ``-w`` option was passed to xgettext.',
        metavar='N', type=int,
    )
    parser.add_argument(
        '-m', '--merge-pofiles',
        dest='mark_not_found_as_absolete',
        action='store_false',
        help='New found msgids not present in the pofile passed at '
             '``--po-filepath`` parameter will be preserved in the new pofile,'
             ' even when are not been found in the current extraction. If this'
             ' argument is not passed, will be marked as obsolete strings.',
    )
    parser.add_argument(
        '-x', '--extensions', dest='extensions',
        default=','.join(
            DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
        ),
        help='md4c extensions used to parse markdown content, separated by'
             ' ``,`` and formatted as pymd4c extension keyword arguments.'
             ' You can see all available at https://github.com/dominickpastore'
             '/pymd4c#parser-option-flags',
    )
    parser.add_argument(
        '-e', '--encoding', dest='encoding', default=None,
        help='Resulting pofile encoding (autodetected by default).',
    )
    parser.add_argument(
        '-a', '--xheaders', dest='xheaders',
        action='store_true',
        help='Include mdpo specification x-headers. These only will be'
             ' included if you do not pass the parameter ``--plaintext``.',
    )
    parser.add_argument(
        '-c', '--include-codeblocks',
        dest='include_codeblocks', action='store_true',
        help='Include all code blocks found inside pofile result. This is'
             ' useful if you want to translate all your blocks of code.'
             ' Equivalent to append \'<!-- mdpo-include-codeblock -->\''
             ' command before each code block.',
    )
    return parser


def parse_options(args=[]):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(0)
    opts, unknown = parser.parse_known_args(args)

    if not sys.stdin.isatty():
        opts.glob_or_content = sys.stdin.read().strip('\n')
    elif isinstance(opts.glob_or_content, list):
        opts.glob_or_content = opts.glob_or_content[0]
    if opts.ignore:
        opts.ignore = parse_list_argument(opts.ignore)
    opts.extensions = opts.extensions.split(',')

    return opts


def run(args=[]):
    opts = parse_options(args)

    kwargs = dict(
        po_filepath=opts.po_filepath,
        ignore=opts.ignore,
        save=opts.save,
        mo_filepath=opts.mo_filepath,
        plaintext=opts.plaintext,
        mark_not_found_as_absolete=opts.mark_not_found_as_absolete,
        extensions=opts.extensions,
        encoding=opts.encoding,
        xheaders=opts.xheaders,
        include_codeblocks=opts.include_codeblocks,
    )
    if isinstance(opts.wrapwidth, int):
        kwargs['wrapwidth'] = opts.wrapwidth

    pofile = markdown_to_pofile(opts.glob_or_content, **kwargs)

    if not opts.quiet:
        sys.stdout.write('%s\n' % pofile.__unicode__())

    return (pofile, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
