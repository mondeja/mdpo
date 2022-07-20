#!/usr/bin/env python

"""md2po command line interface.

See :ref:`md2po CLI<cli:md2po>`.
"""

import argparse
import sys

from mdpo.cli import (
    CLOSE_QUOTE_CHAR,
    OPEN_QUOTE_CHAR,
    add_check_option,
    add_command_alias_argument,
    add_common_cli_first_arguments,
    add_debug_option,
    add_encoding_arguments,
    add_event_argument,
    add_extensions_argument,
    add_nolocation_option,
    add_wrapwidth_argument,
    cli_codespan,
    parse_command_aliases_cli_arguments,
    parse_event_argument,
    parse_metadata_cli_arguments,
)
from mdpo.io import environ
from mdpo.md2po import Md2Po
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


DESCRIPTION = (
    'Utility like xgettext to extract Markdown contents dumping them'
    ' inside PO files.'
)


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'files_or_content', metavar='GLOBS_FILES_OR_CONTENT',
        nargs='*',
        help='Globs to markdown input files, paths to files or Markdown'
             ' content. If not provided, will be read from STDIN.',
    )
    parser.add_argument(
        '-i', '--ignore', dest='ignore', default=[], action='append',
        help='Path to a file to ignore. This argument can be passed multiple'
             ' times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-p', '--po-filepath', '--pofilepath', dest='po_filepath',
        default=None,
        help='Merge new msgids in the po file indicated at this parameter (if'
             f' {cli_codespan("--save")} argument is passed) or use the msgids'
             ' of the file as reference for mark not found as obsoletes if'
             f' {cli_codespan("--merge-pofiles")} parameter is not passed.',
        metavar='OUTPUT_PO_FILEPATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', action='store_true',
        help='Save new found msgids to the po file indicated as parameter'
             f' {cli_codespan("--po-filepath")}. Passing this option without'
             f' defining the argument {cli_codespan("--po-filepath")} will'
              ' raise an error.',
    )
    parser.add_argument(
        '--mo-filepath', '--mofilepath', dest='mo_filepath',
        default=None,
        help='The resulting PO file will be compiled to a mofile and saved in'
             ' the path specified at this parameter.',
        metavar='OUTPUT_MO_FILEPATH',
    )
    parser.add_argument(
        '--plaintext', dest='plaintext', action='store_true',
        help='Do not include markdown markup characters in extracted msgids'
             f' for {cli_codespan("**bold text**", cli=False)},'
             f' {cli_codespan("*italic text*", cli=False)},'
             f' {cli_codespan("``inline code``")} and'
             f' {cli_codespan("[link](target)")}.',
    )
    add_wrapwidth_argument(parser, markup='po')
    parser.add_argument(
        '-m', '--merge-po-files', '--merge-pofiles',
        dest='mark_not_found_as_obsolete',
        action='store_false',
        help='Messages not found which are already stored in the PO file'
             f' passed as {cli_codespan("--po-filepath")} argument will not be'
             ' marked as obsolete.',
    )
    parser.add_argument(
        '-r', '--remove-not-found',
        dest='preserve_not_found',
        action='store_false',
        help='Messages not found which are already stored in the PO file'
             f' passed as {cli_codespan("--po-filepath")} parameter will be'
             ' removed. Only has effect used in combination with'
             f' {cli_codespan("--merge-pofiles")}. If you pass this option,'
             f' {cli_codespan("--merge-po-files")} will be ignored.',
    )
    add_nolocation_option(parser)
    add_extensions_argument(parser)
    add_encoding_arguments(
        parser,
        po_encoding_help='Resulting PO file encoding.',
    )
    parser.add_argument(
        '-a', '--xheader', dest='xheader', action='store_true',
        help='Include in the resulting PO file the mdpo specification'
             ' X-Header "X-Generation", whose value is "mdpo v<version>".',
    )
    parser.add_argument(
        '-c', '--include-codeblocks',
        dest='include_codeblocks', action='store_true',
        help='Include all code blocks found inside PO file result. This is'
             ' useful if you want to translate all your blocks of code.'
             ' Equivalent to append'
             f' {cli_codespan("<!-- mdpo-include-codeblock -->")} command'
             ' before each code block.',
    )
    parser.add_argument(
        '--ignore-msgids', dest='ignore_msgids', default=None,
        help='Path to a plain text file where all msgids to ignore from being'
             ' extracted are located, separated by newlines.',
    )

    # patch for sphinx-argparse-cli compatibility (use Unicode quotation marks)
    example_codespan = (
        f'-d {OPEN_QUOTE_CHAR}Content-Type: text/plain;'
        f' charset=utf-8{CLOSE_QUOTE_CHAR}'
        f' -d {OPEN_QUOTE_CHAR}Language: es{CLOSE_QUOTE_CHAR}'
    )
    metadata_help_example = (
        ' For example, to define UTF-8 encoding and Spanish language use'
        f' {cli_codespan(example_codespan)}.'
    )
    parser.add_argument(
        '-d', '--metadata', dest='metadata', default=[], action='append',
        metavar='Key:Value',
        help='Custom metadata key-value pairs to include in the produced'
             ' PO file. This argument can be passed multiple times.'
             ' If the file contains previous metadata fields, these will'
             ' be updated preserving the values of the already defined.'
             f'{metadata_help_example}',
    )

    add_command_alias_argument(parser)
    add_event_argument(parser)
    add_debug_option(parser)
    add_check_option(parser)
    return parser


def parse_options(args=[]):
    parser = build_parser()
    if '-h' in args or '--help' in args:
        parser.print_help()
        sys.exit(1)
    opts, unknown = parser.parse_known_args(args)

    files_or_content = ''
    if not sys.stdin.isatty():
        files_or_content += sys.stdin.read().strip('\n')
    if isinstance(opts.files_or_content, list) and opts.files_or_content:
        if len(opts.files_or_content) == 1:
            files_or_content += opts.files_or_content[0]
        else:
            files_or_content = opts.files_or_content
    if not files_or_content:
        sys.stderr.write('Files or content to extract not specified\n')
        sys.exit(1)
    opts.files_or_content = files_or_content

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
    opts.events = parse_event_argument(opts.events)
    opts.metadata = parse_metadata_cli_arguments(
        opts.metadata,
    )

    return opts


def run(args=[]):
    with environ(_MDPO_RUNNING='true'):
        opts = parse_options(args)

        init_kwargs = {
            'ignore': opts.ignore,
            'plaintext': opts.plaintext,
            'mark_not_found_as_obsolete': opts.mark_not_found_as_obsolete,
            'preserve_not_found': opts.preserve_not_found,
            'location': opts.location,
            'extensions': opts.extensions,
            'xheader': opts.xheader,
            'include_codeblocks': opts.include_codeblocks,
            'ignore_msgids': opts.ignore_msgids,
            'command_aliases': opts.command_aliases,
            'metadata': opts.metadata,
            'events': opts.events,
            'debug': opts.debug,
            '_check_saved_files_changed': opts.check_saved_files_changed,
        }

        extract_kwargs = {
            'po_filepath': opts.po_filepath,
            'save': opts.save,
            'mo_filepath': opts.mo_filepath,
            'po_encoding': opts.po_encoding,
            'md_encoding': opts.md_encoding,
            'wrapwidth': opts.wrapwidth,
        }

        md2po = Md2Po(opts.files_or_content, **init_kwargs)
        pofile = md2po.extract(**extract_kwargs)

        if not opts.quiet:
            sys.stdout.write(f'{pofile.__unicode__()}\n')

        # pre-commit mode
        if opts.check_saved_files_changed and md2po._saved_files_changed:
            return (pofile, 1)

    return (pofile, 0)


def main():
    raise SystemExit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
