#!/usr/bin/env python

"""mdpo2html command line interface.

See :ref:`mdpo2html CLI<cli:mdpo2html>`.
"""

import argparse
import itertools
import sys

from mdpo.cli import (
    add_check_option,
    add_command_alias_argument,
    add_common_cli_first_arguments,
    add_encoding_arguments,
    add_no_empty_msgstr_option,
    add_no_fuzzy_option,
    add_no_obsolete_option,
    cli_codespan,
    parse_command_aliases_cli_arguments,
)
from mdpo.io import environ
from mdpo.mdpo2html import MdPo2HTML
from mdpo.po import (
    check_empty_msgstrs_in_filepaths,
    check_fuzzy_entries_in_filepaths,
    check_obsolete_entries_in_filepaths,
    paths_or_globs_to_unique_pofiles,
)


DESCRIPTION = 'HTML-produced-from-Markdown file translator using PO files.'


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
    add_common_cli_first_arguments(parser)
    parser.add_argument(
        'filepath_or_content', metavar='FILEPATH_OR_CONTENT',
        nargs='*',
        help='HTML file path or content to translate. If not provided, will be'
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
        help=f'Filepaths to ignore when {cli_codespan("--pofiles")} argument'
             ' value is a glob. This argument can be passed multiple times.',
        metavar='PATH',
    )
    parser.add_argument(
        '-s', '--save', dest='save', default=None,
        help='Saves the output content in file whose path is specified at this'
             ' parameter.', metavar='PATH',
    )
    add_encoding_arguments(parser, markup_encoding='html')
    add_command_alias_argument(parser)
    add_check_option(parser)
    add_no_obsolete_option(parser)
    add_no_fuzzy_option(parser)
    add_no_empty_msgstr_option(parser)
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
    if not filepath_or_content:
        sys.stderr.write('Files or content to translate not specified\n')
        sys.exit(1)
    opts.filepath_or_content = filepath_or_content

    opts.command_aliases = parse_command_aliases_cli_arguments(
        opts.command_aliases,
    )

    opts.pofiles = set(itertools.chain(*opts.pofiles))  # flatten

    return opts


def run(args=frozenset()):
    exitcode = 0
    with environ(_MDPO_RUNNING='true'):
        opts = parse_options(args)

        mdpo2html = MdPo2HTML(
            opts.pofiles,
            ignore=opts.ignore,
            po_encoding=opts.po_encoding,
            command_aliases=opts.command_aliases,
            _check_saved_files_changed=opts.check_saved_files_changed,
        )
        output = mdpo2html.translate(
            opts.filepath_or_content,
            save=opts.save,
            html_encoding=opts.html_encoding,
        )

        if not opts.quiet and not opts.save:
            sys.stdout.write(f'{output}\n')

        if opts.check_saved_files_changed and mdpo2html._saved_files_changed:
            exitcode = 2

        if opts.no_obsolete:
            pofiles = paths_or_globs_to_unique_pofiles(
                opts.pofiles,
                opts.ignore or [],
                po_encoding=opts.po_encoding,
            )
            locations = list(check_obsolete_entries_in_filepaths(
                pofiles,
            ))
            if locations:
                if len(locations) > 2:  # noqa PLR2004
                    sys.stderr.write(
                        f'Found {len(locations)} obsolete entries:\n',
                    )
                    for location in locations:
                        sys.stderr.write(f'{location}\n')
                else:
                    for location in locations:
                        sys.stderr.write(
                            f'Found obsolete entry at {location}\n',
                        )
                exitcode = 3

        if opts.no_fuzzy:
            pofiles = paths_or_globs_to_unique_pofiles(
                opts.pofiles,
                opts.ignore or [],
                po_encoding=opts.po_encoding,
            )
            locations = list(check_fuzzy_entries_in_filepaths(
                pofiles,
            ))
            if locations:
                if len(locations) > 2:  # noqa PLR2004
                    sys.stderr.write(
                        f'Found {len(locations)} fuzzy entries:\n',
                    )
                    for location in locations:
                        sys.stderr.write(f'{location}\n')
                else:
                    for location in locations:
                        sys.stderr.write(
                            f'Found fuzzy entry at {location}\n',
                        )
                exitcode = 4

        if opts.no_empty_msgstr:
            locations = list(check_empty_msgstrs_in_filepaths(
                (opts.po_filepath,),
            ))
            if locations:
                if len(locations) > 2:  # noqa PLR2004
                    sys.stderr.write(
                        f'Found {len(locations)} empty msgstrs:\n',
                    )
                    for location in locations:
                        sys.stderr.write(f'{location}\n')
                else:
                    for location in locations:
                        sys.stderr.write(
                            f'Found empty msgstr at {location}\n',
                        )
                exitcode = 5

    return (output, exitcode)


def main():
    raise SystemExit(run(args=sys.argv[1:])[1])  # pragma: no cover


if __name__ == '__main__':
    main()
