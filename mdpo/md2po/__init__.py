"""Markdown to PO files extractor according to mdpo specification."""

import glob
import os

import md4c
import polib

from mdpo.command import (
    normalize_mdpo_command_aliases,
    parse_mdpo_html_command,
)
from mdpo.event import debug_events, raise_skip_event
from mdpo.io import (
    filter_paths,
    save_file_checking_file_changed,
    to_files_or_content,
)
from mdpo.md import parse_link_references
from mdpo.md4c import (
    DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
    READABLE_BLOCK_NAMES,
)
from mdpo.po import (
    find_entry_in_entries,
    mark_not_found_entries_as_obsoletes,
    po_escaped_string,
    remove_not_found_entries,
)
from mdpo.text import min_not_max_chars_in_a_row, parse_wrapwidth_argument


class Md2Po:
    __slots__ = {
        'filepaths',
        'content',
        'pofile',
        'po_filepath',
        'msgstr',
        'found_entries',
        'disabled_entries',
        'ignore_msgids',
        'command_aliases',
        'mark_not_found_as_obsolete',
        'preserve_not_found',
        'extensions',
        'plaintext',
        'include_codeblocks',
        'metadata',
        'events',

        'location',
        '_current_top_level_block_number',
        '_current_top_level_block_type',
        '_current_markdown_filepath',

        '_current_msgid',
        '_current_tcomment',
        '_current_msgctxt',

        '_disable',
        '_disable_next_line',
        '_enable_next_line',
        '_include_next_codeblock',
        '_disable_next_codeblock',
        '_saved_files_changed',

        '_enterspan_replacer',
        '_leavespan_replacer',

        'bold_start_string',
        'bold_end_string',
        'italic_start_string',
        'italic_start_string_escaped',
        'italic_end_string',
        'italic_end_string_escaped',
        'code_start_string',
        'code_start_string_escaped',
        'code_end_string',
        'code_end_string_escaped',
        'strikethrough_start_string',
        'strikethrough_end_string',
        'latexmath_start_string',
        'latexmath_end_string',
        'latexmathdisplay_start_string',
        'latexmathdisplay_end_string',
        'wikilink_start_string',
        'wikilink_end_string',
        'underline_start_string',
        'underline_end_string',

        '_inside_uspan',
        '_inside_htmlblock',
        '_inside_codeblock',
        '_inside_pblock',
        '_inside_aspan',
        '_inside_liblock',
        '_inside_codespan',
        '_inside_olblock',
        '_inside_hblock',
        '_quoteblocks_deep',
        '_codespan_start_index',
        '_codespan_backticks',
        '_current_aspan_text',
        '_current_aspan_ref_target',
        '_current_wikilink_target',
        '_current_imgspan',
        '_uls_deep',
        '_link_references',
    }

    def __init__(self, files_or_content, **kwargs):
        is_glob, files_or_content = to_files_or_content(files_or_content)
        if is_glob:
            filepaths = []
            for globpath in files_or_content:
                filepaths.extend(glob.glob(globpath))
            self.filepaths = filter_paths(
                filepaths,
                ignore_paths=kwargs.get('ignore', []),
            )
        else:
            self.content = files_or_content

        self.pofile = None
        self.po_filepath = None
        self.msgstr = kwargs.get('msgstr', '')
        self.found_entries = []
        self.disabled_entries = []
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

        self.ignore_msgids = kwargs.get('ignore_msgids', [])
        self.command_aliases = normalize_mdpo_command_aliases(
            kwargs.get('command_aliases', {}),
        )

        self.mark_not_found_as_obsolete = kwargs.get(
            'mark_not_found_as_obsolete', True,
        )
        self.preserve_not_found = kwargs.get('preserve_not_found', True)

        self.location = kwargs.get('location', True)
        # "top level" here because blocks inside blocks are not taken into
        # account for locations
        self._current_top_level_block_number = 0
        self._current_top_level_block_type = None
        self._current_markdown_filepath = None

        self.extensions = kwargs.get(
            'extensions',
            DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
        )
        self.events = {}
        if 'events' in kwargs:
            for event_name, functions in kwargs['events'].items():
                self.events[event_name] = (
                    [functions] if callable(functions) else functions
                )
        if kwargs.get('debug'):
            for event_name, function in debug_events('md2po').items():
                if event_name not in self.events:
                    self.events[event_name] = []
                self.events[event_name].append(function)

        self.plaintext = kwargs.get('plaintext', False)

        self.include_codeblocks = kwargs.get('include_codeblocks', False)

        self._disable = False
        self._disable_next_line = False
        self._enable_next_line = False

        self._include_next_codeblock = False
        self._disable_next_codeblock = False

        self._saved_files_changed = (
            False if kwargs.get('_check_saved_files_changed') else None
        )

        self.metadata = {}

        if not self.plaintext:
            self.bold_start_string = kwargs.get('bold_start_string', '**')
            self.bold_end_string = kwargs.get('bold_end_string', '**')

            self.italic_start_string = kwargs.get('italic_start_string', '*')
            self.italic_start_string_escaped = po_escaped_string(
                self.italic_start_string,
            )

            self.italic_end_string = kwargs.get('italic_end_string', '*')
            self.italic_end_string_escaped = po_escaped_string(
                self.italic_end_string,
            )

            # codespans are built by a indetermined number of 'x' characters
            # so we take only the first
            self.code_start_string = kwargs.get('code_start_string', '`')[0]
            self.code_start_string_escaped = po_escaped_string(
                self.code_start_string,
            )

            self.code_end_string = kwargs.get('code_end_string', '`')[0]
            self.code_end_string_escaped = po_escaped_string(
                self.code_end_string,
            )

            _include_xheaders = kwargs.get('xheaders', False)

            if _include_xheaders:
                self.metadata.update({
                    'x-mdpo-bold-start': self.bold_start_string,
                    'x-mdpo-bold-end': self.bold_end_string,
                    'x-mdpo-italic-start': self.italic_start_string,
                    'x-mdpo-italic-end': self.italic_end_string,
                    'x-mdpo-code-start': self.code_start_string,
                    'x-mdpo-code-end': self.code_end_string,
                })

            self._enterspan_replacer = {
                md4c.SpanType.STRONG.value: self.bold_start_string,
                md4c.SpanType.EM.value: self.italic_start_string,
                md4c.SpanType.CODE.value: self.code_start_string,
            }

            self._leavespan_replacer = {
                md4c.SpanType.STRONG.value: self.bold_end_string,
                md4c.SpanType.EM.value: self.italic_end_string,
                md4c.SpanType.CODE.value: self.code_end_string,
            }

            if 'strikethrough' in self.extensions:
                self.strikethrough_start_string = kwargs.get(
                    'strikethrough_start_string', '~~',
                )
                self._enterspan_replacer[md4c.SpanType.DEL.value] = \
                    self.strikethrough_start_string

                self.strikethrough_end_string = kwargs.get(
                    'strikethrough_end_string', '~~',
                )
                self._leavespan_replacer[md4c.SpanType.DEL.value] = \
                    self.strikethrough_end_string

                if _include_xheaders:
                    self.metadata.update({
                        'x-mdpo-strikethrough-start':
                            self.strikethrough_start_string,
                        'x-mdpo-strikethrough-end':
                            self.strikethrough_end_string,
                    })

            if 'latex_math_spans' in self.extensions:
                self.latexmath_start_string = kwargs.get(
                    'latexmath_start_string', '$',
                )
                self._enterspan_replacer[md4c.SpanType.LATEXMATH.value] = \
                    self.latexmath_start_string

                self.latexmath_end_string = kwargs.get(
                    'latexmath_end_string', '$',
                )
                self._leavespan_replacer[md4c.SpanType.LATEXMATH.value] = \
                    self.latexmath_end_string

                self.latexmathdisplay_start_string = kwargs.get(
                    'latexmathdisplay_start_string', '$$',
                )
                self._enterspan_replacer[
                    md4c.SpanType.LATEXMATH_DISPLAY.value
                ] = self.latexmathdisplay_start_string

                self.latexmathdisplay_end_string = kwargs.get(
                    'latexmathdisplay_end_string', '$$',
                )
                self._leavespan_replacer[
                    md4c.SpanType.LATEXMATH_DISPLAY.value
                ] = self.latexmathdisplay_end_string

                if _include_xheaders:
                    self.metadata.update({
                        'x-mdpo-latexmath-start': self.latexmath_start_string,
                        'x-mdpo-latexmath-end': self.latexmath_end_string,
                        'x-mdpo-latexmathdisplay-start':
                            self.latexmathdisplay_start_string,
                        'x-mdpo-latexmathdisplay-end':
                            self.latexmathdisplay_end_string,
                    })

            if 'wikilinks' in self.extensions:
                self.wikilink_start_string = kwargs.get(
                    'wikilink_start_string', '[[',
                )
                self.wikilink_end_string = kwargs.get(
                    'wikilink_end_string', ']]',
                )

                self._enterspan_replacer[md4c.SpanType.WIKILINK.value] = \
                    self.wikilink_start_string
                self._leavespan_replacer[md4c.SpanType.WIKILINK.value] = \
                    self.wikilink_end_string

                if _include_xheaders:
                    self.metadata.update({
                        'x-mdpo-wikilink-start': self.wikilink_start_string,
                        'x-mdpo-wikilink-end': self.wikilink_end_string,
                    })

            if 'underline' in self.extensions:
                # underline text is standarized with double '_'
                self.underline_start_string = kwargs.get(
                    'underline_start_string', '__',
                )
                self._enterspan_replacer[md4c.SpanType.U.value] = \
                    self.underline_start_string

                self.underline_end_string = kwargs.get(
                    'underline_end_string', '__',
                )
                self._leavespan_replacer[md4c.SpanType.U.value] = \
                    self.underline_end_string

                if _include_xheaders:
                    self.metadata.update({
                        'x-mdpo-underline-start': self.underline_start_string,
                        'x-mdpo-underline-end': self.underline_end_string,
                    })

            # optimization to skip checking for
            # ``self.md4c_generic_parser_kwargs.get('underline')``
            # inside spans
            self._inside_uspan = False

        self._inside_htmlblock = False
        self._inside_codeblock = False
        self._inside_pblock = False
        self._inside_liblock = False
        self._inside_hblock = False
        self._inside_olblock = False
        self._inside_codespan = False

        self._quoteblocks_deep = 0
        self._uls_deep = 0

        self._codespan_start_index = None
        self._codespan_backticks = None

        self._inside_aspan = False
        self._current_aspan_text = ''
        # indicates the target of the current link, which is referenced and
        # extracted without using MD4C, so we can preserve it as referenced
        self._current_aspan_ref_target = None

        self._link_references = None
        self._current_wikilink_target = None
        self._current_imgspan = {}

        if 'metadata' in kwargs:
            self.metadata.update(kwargs['metadata'])

    def _save_msgid(
        self,
        msgid,
        msgstr='',
        tcomment=None,
        msgctxt=None,
        fuzzy=False,
    ):
        if msgid in self.ignore_msgids:
            return
        entry = polib.POEntry(
            msgid=msgid,
            msgstr=msgstr,
            comment=tcomment,
            msgctxt=msgctxt,
            flags=[] if not fuzzy else ['fuzzy'],
        )

        occurrence = None
        if self.location and self._current_markdown_filepath:
            # here could happen a KeyError if someone has aborted an ,
            # enter event, in which case we do not have access to the
            # block type because ``self._current_top_level_block_type is None``
            current_block_name = READABLE_BLOCK_NAMES[
                self._current_top_level_block_type
            ]
            # TODO: when all tests added and the location feature is fully
            #       tested, we could ignore the KeyError event keeping an
            #       incomplete occurrence place string, and raising a warning
            #       if the user has configured an `enter_block` or
            #       `leave_block` event remembering that
            #       `_current_top_level_block_number` and
            #       `_current_top_level_block_type` properties must be handled
            #       accordingly

            occurrence = (
                self._current_markdown_filepath,
                (
                    f'block {self._current_top_level_block_number}'
                    f' ({current_block_name})'
                ),
            )

            if occurrence not in entry.occurrences:
                entry.occurrences.append(occurrence)

        _equal_entry = find_entry_in_entries(
            entry,
            self.pofile,
            compare_obsolete=False,
            compare_msgstr=False,
            compare_occurrences=False,
        )

        if _equal_entry and _equal_entry.msgstr:
            entry.msgstr = _equal_entry.msgstr
            if _equal_entry.fuzzy and not entry.fuzzy:
                entry.flags.append('fuzzy')
        if entry not in self.pofile:
            self.pofile.append(entry)
        self.found_entries.append(entry)

    def _save_current_msgid(self, msgstr='', fuzzy=False):
        # raise 'msgid' event
        if raise_skip_event(
            self.events,
            'msgid',
            self,
            self._current_msgid,
            msgstr,
            self._current_msgctxt,
            self._current_tcomment,
            ['fuzzy'] if fuzzy else [],
        ):
            return

        if self._current_msgid:
            if (not self._disable_next_line and not self._disable) or \
                    self._enable_next_line:
                self._save_msgid(
                    self._current_msgid,
                    msgstr=msgstr or self.msgstr,
                    msgctxt=self._current_msgctxt,
                    tcomment=self._current_tcomment,
                    fuzzy=fuzzy,
                )
            else:
                self.disabled_entries.append(
                    polib.POEntry(
                        msgid=self._current_msgid,
                        msgstr=msgstr or self.msgstr,
                        msgctxt=self._current_msgctxt,
                        tcomment=self._current_tcomment,
                        flags=['fuzzy'] if fuzzy else [],
                    ),
                )
        self._disable_next_line = False
        self._enable_next_line = False
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

    def command(self, mdpo_command, comment, original_command):
        # raise 'command' event
        if raise_skip_event(
            self.events,
            'command',
            self,
            mdpo_command,
            comment,
            original_command,
        ):
            return

        if mdpo_command == 'mdpo-disable-next-line':
            self._disable_next_line = True
        elif mdpo_command == 'mdpo-disable':
            self._disable = True
        elif mdpo_command == 'mdpo-enable':
            self._disable = False
        elif mdpo_command == 'mdpo-enable-next-line':
            self._enable_next_line = True
        elif mdpo_command == 'mdpo-include-codeblock':
            self._include_next_codeblock = True
        elif mdpo_command == 'mdpo-disable-codeblock':
            self._disable_next_codeblock = True
        elif mdpo_command == 'mdpo-disable-codeblocks':
            self.include_codeblocks = False
        elif mdpo_command == 'mdpo-include-codeblocks':
            self.include_codeblocks = True
        elif mdpo_command == 'mdpo-translator':
            if not comment:
                raise ValueError(
                    'You need to specify a string for the'
                    ' extracted comment with the command'
                    f' \'{original_command}\'.',
                )
            self._current_tcomment = comment
        elif mdpo_command == 'mdpo-context':
            if not comment:
                raise ValueError(
                    'You need to specify a string for the'
                    f' context with the command \'{original_command}\'.',
                )
            self._current_msgctxt = comment
        elif mdpo_command == 'mdpo-include':
            if not comment:
                raise ValueError(
                    'You need to specify a message for the'
                    ' comment to include with the command'
                    f' \'{original_command}\'.',
                )
            self._current_msgid = comment
            self._save_current_msgid()

    def _process_command(self, text):
        original_command, comment = parse_mdpo_html_command(text)
        if original_command is None:
            return

        try:
            command = self.command_aliases[original_command]
        except KeyError:  # not custom command
            command = original_command

        # process solved command
        self.command(command, comment, original_command)

    def enter_block(self, block, details):
        # raise 'enter_block' event
        if raise_skip_event(self.events, 'enter_block', self, block, details):
            return

        if block is md4c.BlockType.P:
            self._inside_pblock = True
            if not any([
                self._inside_hblock,
                self._uls_deep,
                self._quoteblocks_deep,
                self._inside_olblock,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.P.value
        elif block is md4c.BlockType.CODE:
            self._inside_codeblock = True
            if not any([
                self._quoteblocks_deep,
                self._uls_deep,
                self._inside_olblock,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.CODE.value
        elif block is md4c.BlockType.LI:
            self._inside_liblock = True
        elif block is md4c.BlockType.UL:
            self._uls_deep += 1
            if self._uls_deep > 1 or self._inside_olblock:
                # changing UL deeep
                self._save_current_msgid()
            elif not any([
                self._quoteblocks_deep,
                self._inside_olblock,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.UL.value
        elif block is md4c.BlockType.H:
            self._inside_hblock = True
            if not any([
                self._quoteblocks_deep,
                self._uls_deep,
                self._inside_olblock,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.H.value
        elif block is md4c.BlockType.QUOTE:
            self._quoteblocks_deep += 1
            if self._inside_liblock:
                self._save_current_msgid()
            if self._quoteblocks_deep == 1:
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.QUOTE.value
        elif block is md4c.BlockType.OL:
            if not any([
                self._quoteblocks_deep,
                self._uls_deep,
                self._inside_olblock,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.OL.value

            if self._inside_olblock or self._uls_deep:
                self._save_current_msgid()
            self._inside_olblock = True
        elif block is md4c.BlockType.HTML:
            self._inside_htmlblock = True
            if not any([
                self._quoteblocks_deep,
                self._inside_olblock,
                self._uls_deep,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.HTML.value
        elif block is md4c.BlockType.TABLE:
            if not any([
                self._quoteblocks_deep,
                self._inside_olblock,
                self._uls_deep,
            ]):
                self._current_top_level_block_number += 1
                self._current_top_level_block_type = md4c.BlockType.TABLE.value

    def leave_block(self, block, details):
        # raise 'leave_block' event
        if raise_skip_event(self.events, 'leave_block', self, block, details):
            return

        if block is md4c.BlockType.CODE:
            self._inside_codeblock = False
            if not self._disable_next_codeblock:
                if self.include_codeblocks or self._include_next_codeblock:
                    self._save_current_msgid()
            self._include_next_codeblock = False
            self._disable_next_codeblock = False
        elif block is md4c.BlockType.HTML:
            self._inside_htmlblock = False
        else:
            if block is md4c.BlockType.P:
                self._inside_pblock = False
            elif block is md4c.BlockType.LI:
                self._inside_liblock = True
            elif block is md4c.BlockType.UL:
                self._uls_deep -= 1
            elif block is md4c.BlockType.H:
                self._inside_hblock = False
            elif block is md4c.BlockType.QUOTE:
                self._quoteblocks_deep -= 1
            elif block is md4c.BlockType.OL:
                self._inside_olblock = False
            self._save_current_msgid()

    def enter_span(self, span, details):
        # raise 'enter_span' event
        if raise_skip_event(self.events, 'enter_span', self, span, details):
            return

        if (span is md4c.SpanType.IMG or span is md4c.SpanType.A) and \
                details['title']:
            self._save_msgid(details['title'][0][1])

    def not_plaintext_enter_span(self, span, details):
        # raise 'enter_span' event
        if raise_skip_event(self.events, 'enter_span', self, span, details):
            return

        # underline spans for double '_' character enters two times
        if not self._inside_uspan:
            if self._inside_aspan:  # span inside link text
                try:
                    self._current_aspan_text += self._enterspan_replacer[
                        span.value
                    ]
                except KeyError:
                    pass
            else:
                try:
                    self._current_msgid += (
                        self._enterspan_replacer[span.value]
                    )
                except KeyError:
                    pass

        if span is md4c.SpanType.A:
            # here resides the logic of discover if the current link
            # is referenced
            if self._link_references is None:
                self._link_references = parse_link_references(self.content)

            self._inside_aspan = True

            current_aspan_href = details['href'][0][1]
            self._current_aspan_ref_target = None

            if details['title']:
                current_aspan_title = details['title'][0][1]
                for target, href, title in self._link_references:
                    if (
                        href == current_aspan_href and
                        title == current_aspan_title
                    ):
                        self._current_aspan_ref_target = target
                        break
            else:
                for target, href, _ in self._link_references:
                    if href == current_aspan_href:
                        self._current_aspan_ref_target = target
                        break

        elif span is md4c.SpanType.CODE:
            self._inside_codespan = True

            # entering a code span, literal backticks encountered inside
            # will be escaped
            #
            # save the index char of the opening backtick
            self._codespan_start_index = len(self._current_msgid) - 1
        elif span is md4c.SpanType.IMG:
            if self._link_references is None:
                self._link_references = parse_link_references(self.content)

            self._current_imgspan['src'] = details['src'][0][1]
            self._current_imgspan['title'] = '' if not details['title'] \
                else details['title'][0][1]
            self._current_imgspan['text'] = ''
        elif span is md4c.SpanType.U:
            self._inside_uspan = True
        elif span is md4c.SpanType.WIKILINK:
            self._current_wikilink_target = details['target'][0][1]

    def leave_span(self, span, details):
        # raise 'leave_span' event
        if raise_skip_event(self.events, 'leave_span', self, span, details):
            return

    def not_plaintext_leave_span(self, span, details):
        # raise 'leave_span' event
        if raise_skip_event(self.events, 'leave_span', self, span, details):
            return

        if not self._inside_uspan:
            if span is md4c.SpanType.WIKILINK:
                self._current_msgid += self._current_wikilink_target
                self._current_wikilink_target = None
            if self._inside_aspan:  # span inside link text
                try:
                    self._current_aspan_text += self._leavespan_replacer[
                        span.value
                    ]
                except KeyError:
                    pass
            else:
                try:
                    self._current_msgid += (
                        self._leavespan_replacer[span.value]
                    )
                except KeyError:
                    pass

        if span is md4c.SpanType.A:
            if self._current_aspan_ref_target:  # referenced link
                self._current_msgid += f'[{self._current_aspan_text}]'
                if self._current_aspan_ref_target != self._current_aspan_text:
                    self._current_msgid += (
                        f'[{self._current_aspan_ref_target}]'
                    )
                self._current_aspan_ref_target = None
            else:
                title = details['title'][0][1] if details['title'] else ''
                if self._current_aspan_text == details['href'][0][1]:
                    # autolink vs link clash (see implementation notes)
                    self._current_msgid += f'<{self._current_aspan_text}'
                    if title:
                        self._current_msgid += f' "{polib.escape(title)}"'
                    self._current_msgid += '>'
                else:
                    title_part = f' "{polib.escape(title)}"' if title else ''
                    href = details['href'][0][1]
                    self._current_msgid += (
                        f'[{self._current_aspan_text}]({href}{title_part})'
                    )
            self._inside_aspan = False
            self._current_aspan_text = ''
        elif span is md4c.SpanType.CODE:
            self._inside_codespan = False
            self._codespan_start_index = None

            # add backticks at the end for escape internal backticks
            if self._inside_aspan:
                self._current_aspan_text += (
                    self._codespan_backticks * self.code_end_string
                )
            else:
                self._current_msgid += (
                    self._codespan_backticks * self.code_end_string
                )
            self._codespan_backticks = None
        elif span is md4c.SpanType.IMG:
            referenced_target, imgspan_title = (None, None)
            imgspan_src = details['src'][0][1]
            if details['title']:
                imgspan_title = details['title'][0][1]
                for target, href, title in self._link_references:
                    if href == imgspan_src and title == imgspan_title:
                        referenced_target = target
                        break
            else:
                for target, href, _ in self._link_references:
                    if href == imgspan_src:
                        referenced_target = target
                        break

            alt_text = self._current_imgspan['text']
            img_markup = f'![{alt_text}]'
            if referenced_target:
                img_markup += f'[{referenced_target}]'
            else:
                img_markup += f'({imgspan_src}'
                if imgspan_title:
                    img_markup += f' "{polib.escape(imgspan_title)}"'
                img_markup += ')'

            self._current_imgspan = {}

            if self._inside_aspan:
                self._current_aspan_text += img_markup
            else:
                self._current_msgid += img_markup
        elif span is md4c.SpanType.U:
            self._inside_uspan = False

    def text(self, block, text):
        # raise 'text' event
        if raise_skip_event(self.events, 'text', self, block, text):
            return

        if not self._inside_htmlblock:
            if not self._inside_codeblock:
                if any([  # softbreaks
                    self._inside_liblock, self._inside_aspan,
                ]) and text == '\n':
                    text = ' '
                if not self.plaintext:
                    if self._current_imgspan:
                        self._current_imgspan['text'] = text
                        return
                    elif self._inside_codespan:
                        # fix backticks for codespan start and end to escape
                        # internal backticks
                        self._codespan_backticks = min_not_max_chars_in_a_row(
                            self.code_start_string,
                            text,
                        ) - 1
                        self._current_msgid = '{}{}{}'.format(
                            self._current_msgid[:self._codespan_start_index],
                            self._codespan_backticks * self.code_start_string,
                            self._current_msgid[self._codespan_start_index:],
                        )
                        if self._inside_aspan:
                            self._current_aspan_text += text
                            return
                    elif self._inside_aspan:
                        self._current_aspan_text += text
                        return
                    elif text == self.italic_start_string:
                        text = self.italic_start_string_escaped
                    elif text == self.code_start_string:
                        text = self.code_start_string_escaped
                    elif text == self.italic_end_string:   # pragma: no cover
                        text = self.italic_end_string_escaped
                    elif text == self.code_end_string:   # pragma: no cover
                        text = self.code_end_string_escaped
                if self._inside_pblock:
                    text = text.replace('\n', ' ')
                if self._current_wikilink_target:
                    if text != self._current_wikilink_target:
                        # not self-referenced wikilink
                        self._current_wikilink_target = (
                            f'{self._current_wikilink_target}|{text}'
                        )
                    return
                self._current_msgid += text
            else:
                if not self._disable_next_codeblock:
                    if self.include_codeblocks or self._include_next_codeblock:
                        self._current_msgid += text
        else:
            self._process_command(text)

    def _dump_link_references(self):
        if self._link_references:
            self._disable_next_line = False
            self._disable = False

            # 'link_reference' event
            pre_events = self.events.get('link_reference')

            for target, href, title in self._link_references:
                if pre_events:
                    skip = False
                    for event in pre_events:
                        if event(self, target, href, title) is False:
                            skip = True
                    if skip:
                        continue

                self._current_msgid = '[{}]:{}{}'.format(
                    target,
                    f' {href}' if href else '',
                    f' "{title}"' if title else '',
                )
                self._save_current_msgid(
                    msgstr=self._current_msgid,
                    fuzzy=True,
                )

    def extract(
        self,
        po_filepath=None,
        save=False,
        mo_filepath=None,
        po_encoding=None,
        md_encoding='utf-8',
        wrapwidth=78,
    ):
        if not po_filepath:
            self.po_filepath = ''

            if save:
                if os.environ.get('_MDPO_RUNNING') == 'true':
                    save_arg = '-s/--save'
                    po_filepath_arg = '-po/--po-filepath'
                else:
                    save_arg, po_filepath_arg = ('save', 'po_filepath')
                raise ValueError(
                    f"The argument '{save_arg}' does not make sense"
                    f" without passing the argument '{po_filepath_arg}'.",
                )
        else:
            self.po_filepath = po_filepath
            if not os.path.exists(po_filepath):
                self.po_filepath = ''

        pofile_kwargs = (
            {'autodetect_encoding': False, 'encoding': po_encoding}
            if po_encoding else {}
        )
        self.pofile = polib.pofile(
            self.po_filepath,
            wrapwidth=parse_wrapwidth_argument(wrapwidth),
            **pofile_kwargs,
        )

        parser = md4c.GenericParser(
            0,
            **{ext: True for ext in self.extensions},
        )

        def _parse(content):
            parser.parse(
                content,
                self.enter_block,
                self.leave_block,
                (
                    self.enter_span if self.plaintext
                    else self.not_plaintext_enter_span
                ),
                (
                    self.leave_span if self.plaintext
                    else self.not_plaintext_leave_span
                ),
                self.text,
            )
            self._dump_link_references()

        if hasattr(self, 'content'):
            _parse(self.content)
        else:
            for filepath in self.filepaths:
                with open(filepath, encoding=md_encoding) as f:
                    self.content = f.read()
                self._current_markdown_filepath = filepath
                _parse(self.content)

                # reset state
                self._disable_next_line = False
                self._disable = False
                self._enable_next_line = False
                self._include_next_codeblock = False
                self._disable_next_codeblock = False
                self._link_references = None
                self._current_top_level_block_number = 0
                self._current_top_level_block_type = None

        if not self.preserve_not_found:
            remove_not_found_entries(
                self.pofile,
                self.found_entries,
            )
        elif self.mark_not_found_as_obsolete:
            mark_not_found_entries_as_obsoletes(
                self.pofile,
                self.found_entries,
            )

        if self.metadata:
            self.pofile.metadata.update(self.metadata)

        if save and po_filepath:
            if self._saved_files_changed is False:
                self._saved_files_changed = save_file_checking_file_changed(
                    po_filepath,
                    str(self.pofile),
                    encoding=self.pofile.encoding,
                )
            else:
                self.pofile.save(fpath=po_filepath)
        if mo_filepath:
            self.pofile.save_as_mofile(mo_filepath)
        return self.pofile


def markdown_to_pofile(
    files_or_content,
    ignore=[],
    msgstr='',
    po_filepath=None,
    save=False,
    mo_filepath=None,
    plaintext=False,
    wrapwidth=78,
    mark_not_found_as_obsolete=True,
    preserve_not_found=True,
    location=True,
    extensions=DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
    po_encoding=None,
    md_encoding='utf-8',
    xheaders=False,
    include_codeblocks=False,
    ignore_msgids=[],
    command_aliases={},
    metadata={},
    events={},
    debug=False,
    **kwargs,
):
    """Extracts all the msgids from a string of Markdown content or a group of
    files.

    Args:
        files_or_content (str, list): Glob path to Markdown files, a list of
            files or a string with Markdown content.
        ignore (list): Paths of files to ignore. Useful when a glob does not
            fit your requirements indicating the files to extract content.
            Also, filename or a dirname can be defined without indicate the
            full path.
        msgstr (str): Default message string for extracted msgids.
        po_filepath (str): File that will be used as :class:`polib.POFile`
            instance where to dump the new msgids and that will be used
            as source checking not found strings that will be marked as
            obsolete if is the case (see ``save`` and
            ``mark_not_found_as_obsolete`` optional parameters).
        save (bool): Save the new content to the PO file indicated in the
            parameter ``po_filepath``. If is enabled and ``po_filepath`` is
            ``None`` a ``ValueError`` will be raised.
        mo_filepath (str): The resulting PO file will be compiled to a MO file
            and saved in the path specified at this parameter.
        plaintext (bool): If you pass ``True`` to this parameter (as default)
                the content will be extracted as is, without markup characters
                included.
                Passing ``plaintext`` as ``False``, extracted msgids
                will contain some markup characters used to appoint the
                location of ```inline code```, ``**bold text**``,
                ``*italic text*`` and ```[links]```, that might be useful
                for you. It depends on the use you are going to give to
                this library activate this mode (``plaintext=False``) or not.
        wrapwidth (int): Wrap width for po file indicated at ``po_filepath``
            parameter. If negative, 0, 'inf' or 'math.inf' the content won't
            be wrapped.
        mark_not_found_as_obsolete (bool): The strings extracted from markdown
            that will not be found inside the provided PO file will be marked
            as obsolete.
        preserve_not_found (bool): The strings extracted from markdown that
            will not be found inside the provided PO file wouldn't be removed.
            Only has effect if ``mark_not_found_as_obsolete`` is ``False``.
        location (bool): Store references of top-level blocks in which are
            found the messages in PO file `#: reference` comments.
        extensions (list): md4c extensions used to parse markdown content,
            formatted as a list of 'pymd4c' keyword arguments. You can see all
            available at `pymd4c repository <https://github.com/dominickpastore
            /pymd4c#parser-option-flags>`_.
        po_encoding (str): Resulting PO file encoding.
        md_encoding (str): Markdown content encoding.
        xheaders (bool): Indicates if the resulting PO file will have mdpo
            x-headers included. These only can be included if the parameter
            ``plaintext`` is ``False``.
        include_codeblocks (bool): Include all code blocks found inside PO file
            result. This is useful if you want to translate all your blocks
            of code. Equivalent to append ``<!-- mdpo-include-codeblock -->``
            command before each code block.
        ignore_msgids (list): List of msgids ot ignore from being extracted.
        command_aliases (dict): Mapping of aliases to use custom mdpo command
            names in comments. The ``mdpo-`` prefix in command names resolution
            is optional. For example, if you want to use ``<!-- mdpo-on -->``
            instead of ``<!-- mdpo-enable -->``, you can pass the dictionaries
            ``{"mdpo-on": "mdpo-enable"}`` or ``{"mdpo-on": "enable"}`` to this
            parameter.
        metadata (dict): Metadata to include in the produced PO file. If the
            file contains previous metadata fields, these will be updated
            preserving the values of the already defined.
        events (dict): Preprocessing events executed during the parsing
            process. You can use these to customize the extraction process.
            Takes functions or list of functions as values. If one of these
            functions returns ``False``, that part of the parsing is skipped
            by md2po (usually a MD4C event). The available events are:

            * ``enter_block(self, block, details)``: Executed when the parsing
              a Markdown block starts.
            * ``leave_block(self, block, details)``: Executed when the parsing
              a Markdown block ends.
            * ``enter_span(self, span, details)``: Executed when the parsing of
              a Markdown span starts.
            * ``leave_span(self, span, details)``: Executed when the parsing of
              a Markdown span ends.
            * ``text(self, block, text)``: Executed when the parsing of text
              starts.
            * ``command(self, mdpo_command, comment, original command)``:
              Executed when a mdpo HTML command is found.
            * ``msgid(self, msgid, msgstr, msgctxt, tcomment, flags)``:
              Executed when a msgid is going to be stored.
            * ``link_reference(self, target, href, title)``: Executed when a
              link reference is going to be stored.

            All ``self`` arguments are an instance of Md2Po parser. You can
            take advanced control of the parsing process manipulating the
            state of the parser. For example, if you want to skip a certain
            msgid to be included, you can do:

            .. code-block:: python

               def msgid_event(self, msgid, *args):
                   if msgid == 'foo':
                       self._disable_next_line = True
        debug (bool): Add events displaying all parsed elements in the
            extraction process.

    Examples:
        >>> content = 'Some text with `inline code`'
        >>> entries = markdown_to_pofile(content, plaintext=True)
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with inline code': ''}
        >>> entries = markdown_to_pofile(content)
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with `inline code`': ''}
        >>> entries = markdown_to_pofile(content, msgstr='Default message')
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with `inline code`': 'Default message'}

    Returns:
        :class:`polib.POFile` Pofile instance with new msgids included.

    Raises
        ValueError: when ``po_filepath`` is ``None`` and ``save`` is ``True``.
    """
    return Md2Po(
        files_or_content,
        ignore=ignore,
        msgstr=msgstr,
        plaintext=plaintext,
        mark_not_found_as_obsolete=mark_not_found_as_obsolete,
        preserve_not_found=preserve_not_found,
        location=location,
        extensions=extensions,
        xheaders=xheaders,
        include_codeblocks=include_codeblocks,
        ignore_msgids=ignore_msgids,
        command_aliases=command_aliases,
        metadata=metadata,
        events=events,
        debug=debug,
        **kwargs,
    ).extract(
        po_filepath=po_filepath,
        save=save,
        mo_filepath=mo_filepath,
        po_encoding=po_encoding,
        md_encoding=md_encoding,
        wrapwidth=wrapwidth,
    )
