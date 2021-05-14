"""Markdown files translator using PO files as reference."""

import re
import textwrap

import md4c
import polib

from mdpo.command import (
    normalize_mdpo_command_aliases,
    parse_mdpo_html_command,
)
from mdpo.io import to_file_content_if_is_file
from mdpo.md import (
    escape_links_titles,
    fixwrap_codespans,
    inline_untexted_links,
    parse_link_references,
)
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.po import (
    paths_or_globs_to_unique_pofiles,
    po_escaped_string,
    pofiles_to_unique_translations_dicts,
)
from mdpo.polib import *  # noqa
from mdpo.text import (
    min_not_max_chars_in_a_row,
    removesuffix,
    wrap_different_first_line_width,
)


class Po2Md:
    __slots__ = (
        'pofiles',
        'output',
        'content',
        'extensions',
        'events',
        'disabled_entries',
        'translated_entries',
        'translations',
        'translations_with_msgctxt',
        'command_aliases',
        'wrapwidth',

        'bold_start_string',
        'bold_start_string_escaped',
        'bold_end_string',
        'bold_end_string_escaped',
        'italic_start_string',
        'italic_start_string_escaped',
        'italic_end_string',
        'italic_end_string_escaped',
        'code_start_string',
        'code_start_string_escaped',
        'code_end_string',
        'code_end_string_escaped',
        'link_start_string',
        'link_end_string',
        'wikilink_start_string',
        'wikilink_end_string',

        # internal config
        '_current_msgid',
        '_current_msgctxt',
        '_current_tcomment',
        '_current_line',
        '_outputlines',
        '_disable_next_line',
        '_disable',
        '_enable_next_line',
        '_enterspan_replacer',
        '_leavespan_replacer',

        # state
        '_inside_htmlblock',
        '_inside_codeblock',
        '_inside_indented_codeblock',
        '_inside_pblock',
        '_inside_liblock',
        '_inside_liblock_first_p',
        '_inside_codespan',
        '_codespan_start_index',
        '_codespan_backticks',
        '_codespan_inside_current_msgid',
        '_inside_quoteblock',
        '_current_aspan_target',
        '_current_aspan_href',
        '_current_imgspan',
        '_current_thead_aligns',
        '_aimg_title_inside_current_msgid',
        '_ul_marks',
        '_ol_marks',
        '_current_list_type',
        '_current_wikilink_target',
        '_link_references',
    )

    def __init__(self, pofiles, ignore=[], po_encoding=None, **kwargs):
        self.pofiles = paths_or_globs_to_unique_pofiles(
            pofiles,
            ignore,
            po_encoding=po_encoding,
        )

        self.extensions = kwargs.get(
            'extensions',
            DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
        )

        self.events = kwargs.get('events', {})

        self._current_msgid = ''
        self._current_msgctxt = None
        self._current_tcomment = None
        self._current_line = ''
        self._outputlines = []

        self._disable_next_line = False
        self._disable = False
        self._enable_next_line = False
        self.disabled_entries = []
        self.translated_entries = []

        self.translations = None
        self.translations_with_msgctxt = None

        self.command_aliases = normalize_mdpo_command_aliases(
            kwargs.get('command_aliases', {}),
        )

        self.wrapwidth = kwargs.get('wrapwidth', 80)

        self.bold_start_string = kwargs.get('bold_start_string', '**')
        self.bold_start_string_escaped = po_escaped_string(
            self.bold_start_string,
        )

        self.bold_end_string = kwargs.get('bold_end_string', '**')
        self.bold_end_string_escaped = po_escaped_string(
            self.bold_end_string,
        )

        self.italic_start_string = kwargs.get('italic_start_string', '*')
        self.italic_start_string_escaped = po_escaped_string(
            self.italic_start_string,
        )

        self.italic_end_string = kwargs.get('italic_end_string', '*')
        self.italic_end_string_escaped = po_escaped_string(
            self.italic_end_string,
        )

        self.code_start_string = kwargs.get('code_start_string', '`')[0]
        self.code_start_string_escaped = po_escaped_string(
            self.code_start_string,
        )

        self.code_end_string = kwargs.get('code_end_string', '`')[0]
        self.code_end_string_escaped = po_escaped_string(
            self.code_end_string,
        )

        self.link_start_string = kwargs.get('link_start_string', '[')
        self.link_end_string = kwargs.get('link_end_string', ']')

        self._enterspan_replacer = {
            md4c.SpanType.STRONG: self.bold_start_string,
            md4c.SpanType.EM: self.italic_start_string,
            md4c.SpanType.CODE: self.code_start_string,
            md4c.SpanType.A: self.link_start_string,
        }

        self._leavespan_replacer = {
            md4c.SpanType.STRONG: self.bold_end_string,
            md4c.SpanType.EM: self.italic_end_string,
            md4c.SpanType.CODE: self.code_end_string,
            md4c.SpanType.A: self.link_end_string,
        }

        if 'wikilinks' in self.extensions:
            self.wikilink_start_string = kwargs.get('link_end_string', '[[')
            self.wikilink_end_string = kwargs.get('link_end_string', ']]')

            self._enterspan_replacer[md4c.SpanType.WIKILINK] = \
                self.wikilink_start_string
            self._leavespan_replacer[md4c.SpanType.WIKILINK] = \
                self.wikilink_end_string

        self._inside_htmlblock = False
        self._inside_codeblock = False
        self._inside_indented_codeblock = False

        self._inside_pblock = False
        self._inside_liblock = False
        # first li block paragraph (li block "title")
        self._inside_liblock_first_p = False

        self._inside_codespan = False
        self._codespan_start_index = None
        self._codespan_backticks = None
        self._codespan_inside_current_msgid = False

        self._inside_quoteblock = False

        self._current_aspan_target = None
        self._current_aspan_href = None
        self._link_references = None
        self._current_imgspan = {}

        # current table head alignments
        self._current_thead_aligns = []

        # if title are found in images of links for the current msgid
        # we need to escape them after translate it because ``polib.unescape``
        # removes the scapes
        self._aimg_title_inside_current_msgid = False

        # current UL marks by nesting levels
        self._ul_marks = []

        # [numerical iterm order, current delimitier] for OL blocks
        self._ol_marks = []

        # current lists type (list nesting): ['ul' or 'ol', [True, False]]
        #   (second parameter is tasklist item or not)
        self._current_list_type = []

        self._current_wikilink_target = None

    def _process_command(self, text):
        command, comment = parse_mdpo_html_command(text)
        if command is None:
            return

        try:
            command = self.command_aliases[command]
        except KeyError:  # not custom command
            pass

        if command == 'mdpo-disable-next-line':
            self._disable_next_line = True
        elif command == 'mdpo-disable':
            self._disable = True
        elif command == 'mdpo-enable':
            self._disable = False
        elif command == 'mdpo-enable-next-line':
            self._enable_next_line = True
        elif comment:
            if command == 'mdpo-context':
                self._current_msgctxt = comment.rstrip()
            elif command == 'mdpo-translator':
                self._current_tcomment = comment.rstrip()

    def _escape_translation(self, text):
        # escape '"' characters inside links and image titles
        if self._aimg_title_inside_current_msgid:
            text = escape_links_titles(
                text, link_start_string=self.link_start_string,
                link_end_string=self.link_end_string,
            )
        # - `[self-referenced-link]` -> <self-referenced-link>
        return inline_untexted_links(
            text,
            link_start_string=self.link_start_string,
            link_end_string=self.link_end_string,
        )

    def _translate_msgid(self, msgid, msgctxt, tcomment):
        try:
            if msgctxt:
                msgstr = self.translations_with_msgctxt[msgctxt][msgid]
            else:
                msgstr = self.translations[msgid]
        except KeyError:
            return msgid
        else:
            self.translated_entries.append(
                polib.POEntry(
                    msgid=msgid,
                    msgctxt=msgctxt,
                    msgstr=msgstr,
                    tcomment=tcomment,
                ),
            )
            return msgstr or msgid

    def _save_current_msgid(self):
        if (not self._disable and not self._disable_next_line) or \
                self._enable_next_line:
            translation = self._translate_msgid(
                self._current_msgid,
                self._current_msgctxt,
                self._current_tcomment,
            )
        else:
            translation = self._current_msgid
            self.disabled_entries.append(
                polib.POEntry(
                    msgid=translation,
                    msgstr='',
                    msgctxt=self._current_msgctxt,
                    tcomment=self._current_tcomment,
                ),
            )

        if not self._inside_codeblock:
            translation = self._escape_translation(translation)
        elif self._inside_indented_codeblock:
            # add 4 spaces before each line including next indented block code
            translation = '    %s' % re.sub('\n', '\n    ', translation)

        if self._inside_liblock or self._inside_quoteblock:
            first_line_width_diff = -2
            if self._inside_liblock:
                if self._current_list_type[-1][0] == 'ul':
                    if self._current_list_type[-1][-1][-1] is True:
                        first_line_width_diff = -6
                else:
                    first_line_width_diff = -3

            if self._codespan_inside_current_msgid:
                lines = fixwrap_codespans(
                    translation.split('\n'),
                    width=self.wrapwidth,
                    first_line_width=self.wrapwidth + first_line_width_diff,
                )
            else:
                lines = wrap_different_first_line_width(
                    translation,
                    width=self.wrapwidth,
                    first_line_width_diff=first_line_width_diff,
                    break_long_words=False,
                )
            translation = '\n'.join(lines)
        elif self._inside_pblock:
            # wrap paragraphs fitting with markdownlint
            if self._codespan_inside_current_msgid:
                # fix codespans wrapping
                lines = fixwrap_codespans(
                    translation.split('\n'),
                    width=self.wrapwidth,
                )
            else:
                lines = textwrap.wrap(
                    translation,
                    width=self.wrapwidth,
                    break_long_words=False,
                )
            translation = '\n'.join(lines) + '\n'
        self._current_line += translation

        self._current_msgid = ''
        self._current_msgctxt = None
        self._current_tcomment = None

        self._disable_next_line = False
        self._enable_next_line = False

        self._codespan_inside_current_msgid = False
        self._aimg_title_inside_current_msgid = False

    def _save_current_line(self):
        # strip all spaces according to unicodedata database ignoring newlines,
        # see https://docs.python.org/3/library/stdtypes.html#str.splitlines
        self._outputlines.append(self._current_line.rstrip(' \v\x0b\f\x0c'))
        self._current_line = ''

    def enter_block(self, block, details):
        # print('ENTER BLOCK', block.name, details)

        if self._inside_quoteblock and (
                not self._current_line or self._current_line[0] != '>'
        ):
            self._current_line += '> '
        if block.value == md4c.BlockType.P:
            self._inside_pblock = True
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = True
            indent = ''

            if self._inside_liblock:
                self._save_current_msgid()
                if self._current_line:
                    self._save_current_line()
                indent += '   ' * len(self._current_list_type)

            if 'fence_char' in details:
                self._current_line += '{}{}'.format(
                    indent,
                    details['fence_char']*3,
                )
            if details['lang']:
                self._current_line += details['lang'][0][1]
            if 'fence_char' not in details:
                self._inside_indented_codeblock = True
            if self._current_line:
                self._save_current_line()
        elif block.value == md4c.BlockType.H:
            self._current_line += '%s ' % ('#' * details['level'])
        elif block.value == md4c.BlockType.LI:
            if self._current_list_type[-1][0] == 'ol':
                # inside OL
                if len(self._ol_marks) > 1:
                    self._save_current_msgid()
                    if not self._ol_marks[-1][0]:
                        self._save_current_line()
                self._ol_marks[-1][0] += 1
                self._current_line += '{}1{} '.format(
                    '   ' * (len(self._current_list_type) - 1),
                    self._ol_marks[-1][1],
                )
                self._current_list_type[-1][-1].append(False)
            else:
                # inside UL
                self._current_line += '{}{} '.format(
                    '   ' * (len(self._current_list_type) - 1),
                    self._ul_marks[-1],
                )
                if details['is_task']:
                    self._current_line += '[%s] ' % details['task_mark']
                self._current_list_type[-1][-1].append(details['is_task'])
            self._inside_liblock = True
            self._inside_liblock_first_p = True
        elif block.value == md4c.BlockType.UL:
            if self._current_list_type:
                self._save_current_msgid()
                self._save_current_line()
            self._current_list_type.append(['ul', []])
            self._ul_marks.append(details['mark'])
        elif block.value == md4c.BlockType.OL:
            self._current_list_type.append(['ol', []])
            self._ol_marks.append([0, details['mark_delimiter']])
        elif block.value == md4c.BlockType.HR:
            if not self._inside_liblock:
                self._current_line += '---\n\n'
            else:
                # inside lists, the separator '---' can't be used
                self._current_line += '***'
        elif block.value == md4c.BlockType.TR:
            self._current_line += '   ' * len(self._current_list_type)
            if self._current_line.startswith('>    '):
                self._current_line = self._current_line.replace('> ', '')
        elif block.value == md4c.BlockType.TH:
            if self._inside_quoteblock:
                if not self._current_line.replace(' ', '') == '>':
                    self._current_line = removesuffix(self._current_line, '> ')
            self._current_line += '| '
            self._current_thead_aligns.append(details['align'].value)
        elif block.value == md4c.BlockType.TD:
            if self._inside_quoteblock:
                if not self._current_line.replace(' ', '') == '>':
                    self._current_line = removesuffix(self._current_line, '> ')
            self._current_line += '| '
        elif block.value == md4c.BlockType.QUOTE:
            if self._inside_liblock:
                self._save_current_msgid()
                self._save_current_line()
            self._inside_quoteblock = True
        elif block.value == md4c.BlockType.TABLE:
            if self._current_list_type and not self._inside_quoteblock:
                if self._current_line:
                    self._save_current_line()
                self._save_current_line()
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = True

    def leave_block(self, block, details):
        # print('LEAVE BLOCK', block.name, details)

        if block.value == md4c.BlockType.P:
            self._save_current_msgid()

            if self._inside_liblock:
                if self._inside_quoteblock:
                    self._current_line = '{}{}'.format(
                        '   ' * len(self._current_list_type),
                        self._current_line,
                    )
                    self._save_current_line()
                else:
                    if self._inside_liblock_first_p:
                        self._inside_liblock_first_p = False
                    else:
                        self._current_line = '\n{}{}'.format(
                            '   ' * len(self._current_list_type),
                            self._current_line,
                        )
                        self._save_current_line()
            else:
                self._save_current_line()

            self._inside_pblock = False
            if self._inside_quoteblock:
                self._current_line = '>'
                self._save_current_line()

        elif block.value == md4c.BlockType.CODE:
            self._save_current_msgid()
            self._inside_codeblock = False
            self._inside_indented_codeblock = False

            indent = ''
            if self._inside_liblock:
                indent += '   ' * len(self._current_list_type)
            if 'fence_char' in details:
                if self._inside_liblock:
                    self._save_current_line()
                self._current_line += '{}{}'.format(
                    indent,
                    details['fence_char']*3,
                )

            self._save_current_line()
            if not self._inside_liblock:
                # prevent two newlines after indented code block
                if 'fence_char' in details:
                    self._save_current_line()
        elif block.value == md4c.BlockType.H:
            self._save_current_msgid()
            if not self._inside_quoteblock:
                self._current_line += '\n'
            else:
                self._current_line += '\n> '
            self._save_current_line()
            if self._inside_quoteblock:
                self._current_line += '> '
        elif block.value == md4c.BlockType.LI:
            self._save_current_msgid()
            self._inside_liblock = False
            if self._current_line:
                self._save_current_line()
        elif block.value == md4c.BlockType.UL:
            self._ul_marks.pop()
            self._current_list_type.pop()
            if self._inside_quoteblock:
                self._current_line += '> '
            if not self._ul_marks and self._outputlines[-1]:
                self._save_current_line()
        elif block.value == md4c.BlockType.OL:
            self._ol_marks.pop()
            self._current_list_type.pop()
            if self._inside_quoteblock:
                self._current_line += '> '
            if not self._ol_marks and self._outputlines[-1]:
                self._save_current_line()
        elif block.value in (md4c.BlockType.TH, md4c.BlockType.TD):
            self._save_current_msgid()
            self._current_line += ' '
        elif block.value == md4c.BlockType.TR:
            if not self._current_thead_aligns:
                self._current_line += '|'
                self._save_current_line()
        elif block.value == md4c.BlockType.THEAD:
            # build thead separator
            thead_separator = ''
            if self._inside_quoteblock:
                _thead_split = re.split(r'[^\\](\|)', self._current_line)
                if self._current_list_type:
                    _thead_split = _thead_split[1:]
                self._current_line += '|'
                thead_separator += '> '
            else:
                self._current_line += '|'
                _thead_split = re.split(r'[^\\](\|)', self._current_line)
                if self._current_list_type:
                    _thead_split = _thead_split[1:-1]
            thead_separator += '| '

            _antepenultimate_thead_i = len(_thead_split) - 2
            for i, title in enumerate(_thead_split):
                if (i % 2) != 0 or i > _antepenultimate_thead_i:
                    continue
                align = self._current_thead_aligns.pop(0)
                thead_separator += '{}-{}'.format(
                    '-' if align in [0, 3] else ':',
                    '-' if align in [0, 1] else ':',
                )

                thead_separator += ' |'
                if i < len(_thead_split) - 3:
                    thead_separator += ' '

            self._current_line += '\n{}{}'.format(
                '   ' * len(self._current_list_type),
                thead_separator,
            )
            self._save_current_line()
        elif block.value == md4c.BlockType.QUOTE:
            if self._outputlines[-1] == '>':
                self._outputlines.pop()
            if not self._inside_liblock:
                self._save_current_line()
            self._inside_quoteblock = False
        elif block.value == md4c.BlockType.TABLE:
            if not self._inside_quoteblock and not self._current_list_type:
                self._save_current_line()
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = False

    def enter_span(self, span, details):
        # print("ENTER SPAN", span.name, details)

        try:
            self._current_msgid += self._enterspan_replacer[span.value]
        except KeyError:
            pass

        if span.value == md4c.SpanType.A:
            if self._link_references is None:
                self._link_references = parse_link_references(self.content)

            self._current_aspan_href = details['href'][0][1]
            self._current_aspan_target = None

            if details['title']:
                current_aspan_title = details['title'][0][1]
                for target, href, title in self._link_references:
                    if (
                        href == self._current_aspan_href and
                        title == current_aspan_title
                    ):
                        self._current_aspan_target = target
                        break
            else:
                for target, href, title in self._link_references:
                    if href == self._current_aspan_href:
                        self._current_aspan_target = target
                        break

        elif span.value == md4c.SpanType.CODE:
            self._inside_codespan = True
            self._codespan_start_index = len(self._current_msgid)-1
            self._codespan_inside_current_msgid = True
        elif span.value == md4c.SpanType.IMG:
            self._current_imgspan['title'] = '' if not details['title'] \
                else details['title'][0][1]
            self._current_imgspan['src'] = details['src'][0][1]
            self._current_imgspan['text'] = ''
        elif span.value == md4c.SpanType.WIKILINK:
            self._current_wikilink_target = details['target'][0][1]

    def leave_span(self, span, details):
        # print("LEAVE SPAN", span.name, details)

        if span.value == md4c.SpanType.WIKILINK:
            self._current_msgid += polib.escape(self._current_wikilink_target)
            self._current_wikilink_target = None

        try:
            self._current_msgid += self._leavespan_replacer[span.value]
        except KeyError:
            pass

        if span.value == md4c.SpanType.A:
            if self._current_aspan_target:
                self._current_msgid += f'[{self._current_aspan_target}]'
                self._current_aspan_target = None
            else:
                if self._current_aspan_href:
                    self._current_msgid += '({}'.format(details['href'][0][1])
                    if details['title']:
                        self._aimg_title_inside_current_msgid = True
                        self._current_msgid += ' "{}"'.format(
                            polib.escape(details['title'][0][1]),
                        )
                    self._current_msgid += ')'
            self._current_aspan_href = None
        elif span.value == md4c.SpanType.CODE:
            self._inside_codespan = False
            self._current_msgid += (
                self._codespan_backticks * self.code_end_string
            )
            self._codespan_backticks = None
        elif span.value == md4c.SpanType.IMG:
            self._current_msgid += '![{}]({}'.format(
                self._current_imgspan['text'],
                self._current_imgspan['src'],
            )
            if self._current_imgspan['title']:
                self._current_msgid += ' "%s"' % polib.escape(
                    self._current_imgspan['title'],
                )
            self._current_msgid += ')'
            self._current_imgspan = {}

    def text(self, block, text):
        # print("TEXT", "'%s'" % text)

        if not self._inside_htmlblock:
            if not self._inside_codeblock:
                if self._inside_liblock and text == '\n':
                    text = ' '
                if self._current_imgspan:
                    self._current_imgspan['text'] = text
                    return
                elif self._inside_codespan:
                    self._codespan_backticks = min_not_max_chars_in_a_row(
                        self.code_start_string,
                        text,
                    ) - 1
                    self._current_msgid = '{}{}{}'.format(
                        self._current_msgid[:self._codespan_start_index],
                        self._codespan_backticks * self.code_start_string,
                        self._current_msgid[self._codespan_start_index:],
                    )
                elif text == self.italic_start_string:
                    text = self.italic_start_string_escaped
                elif text == self.code_start_string:
                    text = self.code_start_string_escaped
                elif text == self.code_end_string:  # pragma: no cover
                    text = self.code_end_string_escaped
                elif text == self.italic_end_string:  # pragma: no cover
                    text = self.italic_end_string_escaped

                if self._inside_pblock:
                    text = text.replace('\n', ' ')
                if text == self._current_aspan_href:
                    # self-referenced wiki or inline link
                    self._current_aspan_href = None

                elif self._current_wikilink_target:
                    if text != self._current_wikilink_target:
                        self._current_wikilink_target = '{}|{}'.format(
                            self._current_wikilink_target, text,
                        )
                    return
                self._current_msgid += text
            else:
                if self._inside_liblock:
                    indent = '   ' * len(self._current_list_type)
                    if self._current_line[:len(indent)+1] != indent:
                        self._current_line += indent
                self._current_msgid += text
        else:
            self._process_command(text)

    def _append_link_references(self):
        if self._link_references:
            self._disable_next_line = False
            self._disable = False

            pre_event = self.events.get('link_reference')

            _references_added = []  # don't repeat references
            for target, href, title in self._link_references:

                # 'link_reference' event
                if pre_event and pre_event(self, target, href, title) is False:
                    continue

                href_part = '{}{}'.format(
                    f' {href}' if href else '',
                    f' "{title}"' if title else '',
                )
                if href_part in _references_added:
                    continue

                msgid = '{}{}'.format(f'[{target}]:', href_part)
                self._outputlines.append(
                    self._translate_msgid(msgid, None, None),
                )
                _references_added.append(href_part)
            self._outputlines.append('')

    def translate(
        self,
        filepath_or_content,
        save=None,
        md_encoding='utf-8',
    ):
        self.content = to_file_content_if_is_file(
            filepath_or_content,
            encoding=md_encoding,
        )

        self.translations, self.translations_with_msgctxt = (
            pofiles_to_unique_translations_dicts(self.pofiles)
        )

        parser = md4c.GenericParser(
            0,
            **{ext: True for ext in self.extensions},
        )
        parser.parse(
            self.content,
            self.enter_block,
            self.leave_block,
            self.enter_span,
            self.leave_span,
            self.text,
        )
        self._append_link_references()

        self._disable_next_line = False
        self._disable = False
        self._enable_next_line = False
        self._link_references = None

        self.output = '\n'.join(self._outputlines)

        if save:
            with open(save, 'w', encoding=md_encoding) as f:
                f.write(self.output)

        return self.output


def pofile_to_markdown(
    filepath_or_content,
    pofiles,
    ignore=[],
    save=None,
    md_encoding='utf-8',
    po_encoding=None,
    command_aliases={},
    wrapwidth=80,
    events={},
    **kwargs,
):
    r"""Translate Markdown content or a file using PO files for message replacing.

    This implementation reproduces the same valid Markdown output, given the
    provided AST, with replaced translations, but doesn't rebuilds the same
    input format as Markdown is just a subset of HTML.

    Args:
        filepath_or_content (str): Markdown filepath or content to translate.
        pofiles (str, list) Glob or list of globs matching a set of pofiles
            from where to extract messages to make the replacements translating
            strings.
        ignore (list): Paths of pofiles to ignore. Useful when a glob does not
            fit your requirements indicating the files to extract content.
            Also, filename or a dirname can be defined without indicate the
            full path.
        save (str): Saves the output content in file whose path is specified
            at this parameter.
        md_encoding (str): Markdown content encoding.
        po_encoding (str): PO files encoding. If you need different encodings
            for each file, you must define it in the "Content-Type" field of
            each PO file metadata, in the form
            ``"Content-Type: text/plain; charset=<ENCODING>\n"``.
        command_aliases (dict): Mapping of aliases to use custom mdpo command
            names in comments. The ``mdpo-`` prefix in command names resolution
            is optional. For example, if you want to use ``<!-- mdpo-on -->``
            instead of ``<!-- mdpo-enable -->``, you can pass the dictionaries
            ``{"mdpo-on": "mdpo-enable"}`` or ``{"mdpo-on": "enable"}`` to this
            parameter.
        wrapwidth (int): Maximum width used rendering the Markdown output.
        events (dict): Preprocessing events executed during the translation
            process. You can use these to customize the output. Takes functions
            are values. If one of these functions returns ``False``, that part
            of the translation process is skipped by po2md. The available
            events are:

            * ``link_reference``: Executed when each reference link is being
                written in the output (at the end of the translation process).

    Returns:
        str: Markdown output file with translated content.
    """
    return Po2Md(
        pofiles,
        ignore=ignore,
        po_encoding=po_encoding,
        command_aliases=command_aliases,
        wrapwidth=wrapwidth,
        events=events,
        **kwargs,
    ).translate(
        filepath_or_content,
        save=save,
        md_encoding=md_encoding,
    )
