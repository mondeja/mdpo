#!/usr/bin/env python

"""md2po command line interface."""

import argparse
import sys

from mdpo.cli import (
    add_common_cli_first_arguments,
    add_common_cli_latest_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_extensions_argument,
    add_nolocation_option,
    add_pre_commit_option,
    parse_command_aliases_cli_arguments,
    parse_metadata_cli_arguments,
)
from mdpo.context import environ
from mdpo.md2po import Md2Po
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


DESCRIPTION = (
    'Utility like xgettext to extract Markdown content dumping it'
    ' inside PO files.'
)


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'glob_or_content', metavar='GLOB_OR_CONTENT',
        nargs='*',
        help='Glob to markdown input files or markdown content as string.'
             ' If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-i', '--ignore', dest='ignore', default=[], action='append',
        help='Filepath to ignore when \'GLOB_OR_CONTENT\' argument'
             ' is a glob. This argument can be passed multiple times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-po', '--po-filepath', '--pofilepath', dest='po_filepath',
        default=None,
        help='Merge new msgids in the po file indicated at this parameter (if'
             ' \'--save\' argument is passed) or use the msgids of the file as'
             ' reference for mark not found as obsoletes if'
             ' \'--merge-pofiles\' parameter is not passed.',
        metavar='OUTPUT_PO_FILEPATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', action='store_true',
        help='Save new found msgids to the po file'
             ' indicated as parameter \'-po/--po-filepath\'.'
             ' Passing this option without defining the argument'
             ' \'-po/--po-filepath\' will raise an error.',
    )
    parser.add_argument(
        '-mo', '--mo-filepath', '--mofilepath', dest='mo_filepath',
        default=None,
        help='The resulting PO file will be compiled to a mofile and saved in'
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
        '-w', '--wrapwidth', dest='wrapwidth', metavar='N/inf', type=str,
        default='78',
        help='Wrap width for po file indicated at \'-po/--po-filepath\''
             ' parameter. Only useful when the \'-w\' option was passed to'
             ' xgettext. You can use the values \'0\' and \'inf\' for infinite'
             ' width.',
    )
    parser.add_argument(
        '-m', '--merge-po-files', '--merge-pofiles',
        dest='mark_not_found_as_obsolete',
        action='store_false',
        help='Messages not found which are already stored in the PO file'
             ' passed as \'-po/--po-filepath\' argument will not be marked as'
             ' obsolete.',
    )
    parser.add_argument(
        '-r', '--remove-not-found',
        dest='preserve_not_found',
        action='store_false',
        help='Messages not found which are already stored in the PO file'
             ' passed as \'-po/--po-filepath\' parameter will be removed.'
             ' Only has effect used in combination with \'--merge-pofiles\'.',
    )
    add_nolocation_option(parser)
    add_extensions_argument(parser)
    add_encoding_arguments(
        parser,
        po_encoding_help='Resulting PO file encoding.',
    )
    parser.add_argument(
        '-a', '--xheaders', dest='xheaders',
        action='store_true',
        help='Include mdpo specification x-headers. These only will be'
             ' included if you do not pass the parameter \'--plaintext\'.',
    )
    parser.add_argument(
        '-c', '--include-codeblocks',
        dest='include_codeblocks', action='store_true',
        help='Include all code blocks found inside PO file result. This is'
             ' useful if you want to translate all your blocks of code.'
             ' Equivalent to append \'<!-- mdpo-include-codeblock -->\''
             ' command before each code block.',
    )
    parser.add_argument(
        '--ignore-msgids', dest='ignore_msgids', default=None,
        help='Path to a plain text file where all msgids to ignore from being'
             ' extracted are located, separated by newlines.',
    )
    parser.add_argument(
        '-d', '--metadata', dest='metadata', default=[], action='append',
        metavar='Key:Value',
        help='Custom metadata key-value pairs to include in the produced'
             ' PO file. This argument can be passed multiple times.'
             ' If the file contains previous metadata fields, these will'
             ' be updated preserving the values of the already defined.'
             ' For example, to define utf-8 encoding and Spanish language use'
             ' \'-d "Content-Type: text/plain; charset=utf-8"'
             ' -d "Language: es"\'.',
    )
    add_common_cli_latest_arguments(parser)
    add_debug_option(parser)
    add_pre_commit_option(parser)
    return parser


def parse_options(args=[]):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(1)
    opts, unknown = parser.parse_known_args(args)

    glob_or_content = ''
    if not sys.stdin.isatty():
        glob_or_content += sys.stdin.read().strip('\n')
    if isinstance(opts.glob_or_content, list) and opts.glob_or_content:
        glob_or_content += opts.glob_or_content[0]
    opts.glob_or_content = glob_or_content

    if opts.extensions is None:
        opts.extensions = DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS

    if opts.ignore_msgids is not None:
        with open(opts.ignore_msgids) as f:
            opts.ignore_msgids = f.read().splitlines()
    else:
        opts.ignore_msgids = []

    opts.command_aliases = parse_command_aliases_cli_arguments(
        opts.command_aliases,
    )
    opts.metadata = parse_metadata_cli_arguments(
        opts.metadata,
    )

    return opts


def run(args=[]):
    with environ(_MDPO_RUNNING='true'):
        opts = parse_options(args)

        init_kwargs = dict(
            ignore=opts.ignore,
            plaintext=opts.plaintext,
            mark_not_found_as_obsolete=opts.mark_not_found_as_obsolete,
            preserve_not_found=opts.preserve_not_found,
            location=opts.location,
            extensions=opts.extensions,
            xheaders=opts.xheaders,
            include_codeblocks=opts.include_codeblocks,
            ignore_msgids=opts.ignore_msgids,
            command_aliases=opts.command_aliases,
            metadata=opts.metadata,
            debug=opts.debug,
            _check_saved_files_changed=opts.check_saved_files_changed,
        )

        extract_kwargs = dict(
            po_filepath=opts.po_filepath,
            save=opts.save,
            mo_filepath=opts.mo_filepath,
            po_encoding=opts.po_encoding,
            md_encoding=opts.md_encoding,
            wrapwidth=opts.wrapwidth,
        )

        md2po = Md2Po(opts.glob_or_content, **init_kwargs)
        pofile = md2po.extract(**extract_kwargs)

        if not opts.quiet:
            sys.stdout.write(pofile.__unicode__() + '\n')

        # pre-commit mode
        if (  # pragma: no cover
            opts.check_saved_files_changed and md2po._saved_files_changed
        ):
            return (pofile, 1)

    return (pofile, 0)


def main():
    sys.exit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
