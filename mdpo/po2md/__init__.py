"""Markdown files translator using pofiles as reference."""

import glob
import re
import textwrap

import md4c
import polib

from mdpo.command import parse_mdpo_html_command
from mdpo.io import filter_paths, to_file_content_if_is_file
from mdpo.md import (
    escape_links_titles,
    fixwrap_codespans,
    inline_untexted_links,
)
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.po import po_escaped_string
from mdpo.polib import *  # noqa
from mdpo.text import min_not_max_chars_in_a_row


class Po2Md:
    def __init__(self, pofiles, ignore=[], po_encoding=None, **kwargs):
        self.pofiles = [
            polib.pofile(pofilepath, encoding=po_encoding) for pofilepath in
            filter_paths(glob.glob(pofiles), ignore_paths=ignore)
        ]

        self.extensions = kwargs.get(
            'extensions',
            DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
        )

        self._current_msgid = ''
        self._current_msgctxt = None
        self._current_line = ''
        self._outputlines = []

        self._disable_next_line = False
        self._disable = False
        self._enable_next_line = False
        self.disabled_entries = []

        self.translations = None
        self.translations_with_msgctxt = None

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

        self._bold_italic_context = False

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

        self._inside_codespan = False
        self._codespan_start_index = None
        self._codespan_backticks = None
        self._codespan_inside_current_msgid = False

        self._inside_quoteblock = False

        self._current_aspan_href = None
        self._current_imgspan = {}

        # current table head alignments
        self._current_thead_aligns = []

        # if title are found in images of links for the current msgid,
        # we need to escape them after translate it because ``polib.unescape``
        # removes the scapes
        self._aimg_title_inside_current_msgid = False

        # current UL marks by nesting levels
        self._ul_marks = []

        # [numerical iterm order, current delimitier] for OL blocks
        self._current_ol_delimiters = []

        self._current_wikilink_target = None

    def _process_command(self, text):
        command, comment = parse_mdpo_html_command(text)
        if command is None:
            return

        if command == 'disable-next-line':
            self._disable_next_line = True
        elif command == 'disable':
            self._disable = True
        elif command == 'enable':
            self._disable = False
        elif command == 'enable-next-line':
            self._enable_next_line = True
        elif command == 'context' and comment:
            self._current_msgctxt = comment.strip(' ')

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

    def _translate_msgid(self, msgid, msgctxt):
        try:
            if msgctxt:
                response = self.translations_with_msgctxt[msgctxt][msgid]
            else:
                response = self.translations[msgid]
        except KeyError:
            response = msgid
        return response or msgid

    def _save_current_msgid(self):
        if (not self._disable and not self._disable_next_line) or \
                self._enable_next_line:
            translation = self._translate_msgid(
                self._current_msgid,
                self._current_msgctxt,
            )
        else:
            translation = self._current_msgid
            self.disabled_entries.append(
                polib.POEntry(
                    msgid=translation,
                    msgstr='',
                    msgctxt=self._current_msgctxt,
                ),
            )

        if not self._inside_codeblock:
            translation = self._escape_translation(translation)

        elif self._inside_indented_codeblock:
            # add 4 spaces before each line including next indented block code
            translation = '    %s' % re.sub('\n', '\n    ', translation)
        if self._inside_liblock:
            translation = '\n'.join(textwrap.wrap(translation, width=79))
        if self._inside_pblock:
            # wrap paragraphs fitting with markdownlint
            if self._codespan_inside_current_msgid:
                # fix codespans wrapping
                lines = fixwrap_codespans(translation.split('\n'))
            else:
                lines = textwrap.wrap(translation, width=80)
            for line in lines:
                self._current_line += '%s\n' % polib.unescape(line)
        else:
            self._current_line += polib.unescape(translation)
        self._current_msgid = ''
        self._current_msgctxt = None

        self._disable_next_line = False
        self._enable_next_line = False

        self._codespan_inside_current_msgid = False
        self._aimg_title_inside_current_msgid = False

    def _save_current_line(self):
        self._outputlines.append(self._current_line.rstrip(' '))
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
            if 'fence_char' in details:
                self._current_line += '%s' % (details['fence_char']*3)
            if details['lang']:
                self._current_line += details['lang'][0][1]
            if 'fence_char' not in details:
                self._inside_indented_codeblock = True
            if self._current_line:
                self._save_current_line()
        elif block.value == md4c.BlockType.H:
            self._current_line += '%s ' % ('#' * details['level'])
        elif block.value == md4c.BlockType.LI:
            if self._current_ol_delimiters:
                # inside OL
                if len(self._current_ol_delimiters) > 1:
                    self._save_current_msgid()
                    if not self._current_ol_delimiters[-1][0]:
                        self._save_current_line()
                self._current_ol_delimiters[-1][0] += 1
                self._current_line += '%s%d%s ' % (
                    '   ' * (len(self._current_ol_delimiters) - 1),
                    self._current_ol_delimiters[-1][0],
                    self._current_ol_delimiters[-1][1],
                )
            else:
                # inside UL
                self._current_line += '{}{} '.format(
                    '  ' * (len(self._ul_marks) - 1), self._ul_marks[-1],
                )
                if details['is_task']:
                    self._current_line += '[%s] ' % details['task_mark']
            self._inside_liblock = True
        elif block.value == md4c.BlockType.UL:
            if len(self._ul_marks) > 0:
                self._save_current_msgid()
                self._save_current_line()
            self._ul_marks.append(details['mark'])
        elif block.value == md4c.BlockType.OL:
            self._current_ol_delimiters.append([0, details['mark_delimiter']])
        elif block.value == md4c.BlockType.HR:
            self._current_line += '---'
            if not self._inside_liblock:
                self._current_line += '\n\n'
        elif block.value == md4c.BlockType.TH:
            self._current_line += '| '
            self._current_thead_aligns.append(details['align'].value)
        elif block.value == md4c.BlockType.TD:
            self._current_line += '| '
        elif block.value == md4c.BlockType.QUOTE:
            self._inside_quoteblock = True
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = True

    def leave_block(self, block, details):
        # print('LEAVE BLOCK', block.name, details)

        if block.value == md4c.BlockType.P:
            self._save_current_msgid()
            if not self._inside_liblock:
                self._save_current_line()
            self._inside_pblock = False
        elif block.value == md4c.BlockType.CODE:
            self._save_current_msgid()
            self._inside_codeblock = False
            self._inside_indented_codeblock = False
            if 'fence_char' in details:
                self._current_line += '%s' % (details['fence_char']*3)
            self._save_current_line()
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
            self._save_current_line()
        elif block.value == md4c.BlockType.UL:
            self._ul_marks.pop()
            if self._inside_quoteblock:
                self._current_line += '> '
            if not self._ul_marks:
                self._save_current_line()
        elif block.value == md4c.BlockType.OL:
            self._current_ol_delimiters.pop()
            if self._inside_quoteblock:
                self._current_line += '> '
            if not self._current_ol_delimiters:
                self._save_current_line()
        elif block.value in (md4c.BlockType.TH, md4c.BlockType.TD):
            self._save_current_msgid()
            self._current_line += ' '
        elif block.value == md4c.BlockType.TR:
            if not self._current_thead_aligns:
                self._current_line += '|'
                self._save_current_line()
        elif block.value == md4c.BlockType.THEAD:
            self._current_line += '|'

            # build thead separator
            thead_separator = '| '
            _thead_split = re.split(r'[^\\](\|)', self._current_line)
            for i, title in enumerate(_thead_split):
                if (i % 2) != 0 or i > len(_thead_split) - 2:
                    continue
                title_length = len(title)-3
                if i == 0:
                    title_length -= 1
                title_length = max(3, title_length)
                align = self._current_thead_aligns.pop(0)
                if align in [0, 3]:
                    thead_separator += '-'
                else:
                    thead_separator += ':'
                thead_separator += ('-' * title_length)

                if align in [0, 1]:
                    thead_separator += '-'
                else:
                    thead_separator += ':'
                thead_separator += ' |'
                if i < len(_thead_split) - 3:
                    thead_separator += ' '

            self._current_line += '\n%s' % thead_separator
            self._save_current_line()
        elif block.value == md4c.BlockType.QUOTE:
            self._current_line += '> '
        elif block.value == md4c.BlockType.TABLE:
            self._save_current_line()
        elif block.value == md4c.BlockType.DOC:
            pass
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = False

    def enter_span(self, span, details):
        # print("ENTER SPAN", span.name, details)

        try:
            self._current_msgid += self._enterspan_replacer[span.value]
        except KeyError:
            pass

        if span.value == md4c.SpanType.A:
            self._current_aspan_href = details['href'][0][1]
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
            if self._current_aspan_href:
                # is not self-referenced link
                self._current_msgid += '(%s' % self._current_aspan_href

                if details['title']:
                    self._aimg_title_inside_current_msgid = True
                    self._current_msgid += ' "%s"' % polib.escape(
                        details['title'][0][1],
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
            self._current_msgid += polib.escape(
                '![{}]({}'.format(
                    self._current_imgspan['text'],
                    self._current_imgspan['src'],
                ),
            )
            if self._current_imgspan['title']:
                self._current_msgid += ' "%s"' % (
                    polib.escape(self._current_imgspan['title'])
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
                if self._current_aspan_href:
                    if text == self._current_aspan_href:
                        # self-referenced link
                        self._current_aspan_href = None
                elif self._current_wikilink_target:
                    if text != self._current_wikilink_target:
                        self._current_wikilink_target = '{}|{}'.format(
                            self._current_wikilink_target, text,
                        )
                    return
                self._current_msgid += polib.escape(text)
            else:
                self._current_msgid += text
        else:
            self._process_command(text)

    def translate(self, filepath_or_content, save=None, md_encoding='utf-8'):
        content = to_file_content_if_is_file(
            filepath_or_content,
            encoding=md_encoding,
        )

        self.translations = {}
        self.translations_with_msgctxt = {}
        for pofile in self.pofiles:
            for entry in pofile:
                if entry.msgctxt:
                    if entry.msgctxt not in self.translations_with_msgctxt:
                        self.translations_with_msgctxt[entry.msgctxt] = {}
                    self.translations_with_msgctxt[
                        entry.msgctxt
                    ][entry.msgid] = entry.msgstr
                else:
                    self.translations[entry.msgid] = entry.msgstr

        parser = md4c.GenericParser(
            0,
            **{ext: True for ext in self.extensions},
        )
        parser.parse(
            content,
            self.enter_block,
            self.leave_block,
            self.enter_span,
            self.leave_span,
            self.text,
        )
        self._disable_next_line = False
        self._disable = False
        self._enable_next_line = False

        self.output = '\n'.join(self._outputlines)

        if save:
            with open(save, 'w', encoding=md_encoding) as f:
                f.write(self.output)

        return self.output


def pofile_to_markdown(
    filepath_or_content, pofiles, ignore=[],
    save=None, md_encoding='utf-8', po_encoding=None, **kwargs,
):
    r"""Translate Markdown content or a file using pofiles for message replacing.

    Args:
        filepath_or_content (str): Markdown filepath or content to translate.
        pofiles (str): Glob matching a set of pofiles from where to extract
            references to make the replacements translating strings.
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

    Returns:
        str: Markdown output file with translated content.
    """
    return Po2Md(
        pofiles, ignore=ignore, po_encoding=po_encoding,
        **kwargs,
    ).translate(
        filepath_or_content, save=save, md_encoding=md_encoding,
    )
