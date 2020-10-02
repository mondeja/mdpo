"""Markdown files translator using pofiles as reference."""

import glob
import re

import md4c
import polib

from mdpo.io import (
    filter_paths,
    to_file_content_if_is_file,
)
from mdpo.md import (
    escape_links_titles,
    fixwrap_codespans,
    inline_untexted_links,
)
from mdpo.md4c import (
    DEFAULT_MD4C_FLAGS,
    parse_md4c_flags_string,
)
from mdpo.po import build_po_escaped_string
from mdpo.text import min_not_max_chars_in_a_row


class Po2Md:
    def __init__(self, pofiles, ignore=[], **kwargs):
        self.pofiles = [polib.pofile(pofilepath) for pofilepath in
                        filter_paths(glob.glob(pofiles), ignore_paths=ignore)]

        self.flags, self.modes = parse_md4c_flags_string(
            kwargs.get('flags', DEFAULT_MD4C_FLAGS))

        self._current_msgid = ''
        self._current_line = ''
        self._outputlines = []

        self.bold_start_string = kwargs.get('bold_start_string', '**')
        self.bold_start_string_escaped = build_po_escaped_string(
            self.bold_start_string)

        self.bold_end_string = kwargs.get('bold_end_string', '**')
        self.bold_end_string_escaped = build_po_escaped_string(
            self.bold_end_string)

        self.italic_start_string = kwargs.get('italic_start_string', '*')
        self.italic_start_string_escaped = build_po_escaped_string(
            self.italic_start_string)

        self.italic_end_string = kwargs.get('italic_end_string', '*')
        self.italic_end_string_escaped = build_po_escaped_string(
            self.italic_end_string)

        self._bold_italic_context = False

        self.code_start_string = kwargs.get('code_start_string', '`')[0]
        self.code_start_string_escaped = build_po_escaped_string(
            self.code_start_string)

        self.code_end_string = kwargs.get('code_end_string', '`')[0]
        self.code_end_string_escaped = build_po_escaped_string(
            self.code_end_string)

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

        if self.modes['wikilinks']:
            self.wikilink_start_string = kwargs.get('link_end_string', '[[')
            self.wikilink_end_string = kwargs.get('link_end_string', ']]')

            self._enterspan_replacer[md4c.SpanType.WIKILINK] = \
                self.wikilink_start_string
            self._leavespan_replacer[md4c.SpanType.WIKILINK] = \
                self.wikilink_end_string

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

        # OL blocks are not fully supported by md4c. We can rebuilt them
        # without nesting and using a basic counter
        self._current_ol_delimitier = None
        self._ol_items_counter = 0

        self._current_wikilink_target = None

    def _escape_translation(self, text):
        # escape '"' characters inside links and image titles
        if self._aimg_title_inside_current_msgid:
            text = escape_links_titles(
                text, link_start_string=self.link_start_string,
                link_end_string=self.link_end_string)
        # - `[self-referenced-link]` -> <self-referenced-link>
        return inline_untexted_links(text,
                                     link_start_string=self.link_start_string,
                                     link_end_string=self.link_end_string)

    def _translate_msgid(self, msgid):
        try:
            response = self.translations[msgid]
        except KeyError:
            response = msgid
        return response

    def _save_current_msgid(self):
        if self._current_msgid:
            translation = self._escape_translation(
                self._translate_msgid(self._current_msgid))
            if self._inside_liblock:
                translation = '\n'.join(polib.wrap(translation, width=79))
            if self._inside_pblock:
                # wrap paragraphs fitting with markdownlint
                lines = polib.wrap(translation, width=80)
                if self._codespan_inside_current_msgid:
                    # fix codespans wrapping
                    lines = fixwrap_codespans(lines)
                for line in lines:
                    self._current_line += '%s\n' % polib.unescape(line)
            else:
                self._current_line += polib.unescape(translation)
            self._current_msgid = ''
        self._codespan_inside_current_msgid = False
        self._aimg_title_inside_current_msgid = False

    def _save_current_line(self, times=1, _time_number=1):
        self._outputlines.append(self._current_line.rstrip(" "))
        self._current_line = ''
        if _time_number < times:
            self._save_current_line(times=times, _time_number=_time_number+1)

    def enter_block(self, block, details):
        # print("ENTER BLOCK", block.name, details)
        if self._inside_quoteblock and (
                not self._current_line or self._current_line[0] != ">"):
            self._current_line += "> "
        if block.value == md4c.BlockType.P:
            self._inside_pblock = True
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = True
            if details['fence_char'] and details['fence_char'] != '\x00':
                self._current_line += '%s' % (details['fence_char']*3)
            if details["lang"]:
                self._current_line += details["lang"][0][1]
            # ``fence_char`` -> None == '\x00' is pymd4c "bug":
            # https://github.com/dominickpastore/pymd4c/pull/11
            if not details["fence_char"] or details["fence_char"] == '\x00':
                self._inside_indented_codeblock = True
            self._save_current_line()
        elif block.value == md4c.BlockType.H:
            self._current_line += '%s ' % ('#' * details['level'])
        elif block.value == md4c.BlockType.LI:
            if self._current_ol_delimitier:
                # inside OL
                self._ol_items_counter += 1
                self._current_line += '%d%s ' % (self._ol_items_counter,
                                                 self._current_ol_delimitier)
            else:
                # inside UL
                self._current_line += "%s%s " % (
                    "  " * (len(self._ul_marks) - 1), self._ul_marks[-1])
                if details["is_task"]:
                    self._current_line += "[%s] " % details["task_mark"]
            self._inside_liblock = True
        elif block.value == md4c.BlockType.UL:
            if len(self._ul_marks) > 0:
                self._save_current_msgid()
                self._save_current_line()
            self._ul_marks.append(details["mark"])
        elif block.value == md4c.BlockType.OL:
            self._current_ol_delimitier = details["mark_delimiter"]
        elif block.value == md4c.BlockType.HR:
            self._current_line += '---'
            if not self._inside_liblock:
                self._current_line += "\n\n"
        elif block.value == md4c.BlockType.TH:
            self._current_line += '| '
            self._current_thead_aligns.append(details['align'].value)
        elif block.value == md4c.BlockType.TD:
            self._current_line += '| '
        elif block.value == md4c.BlockType.QUOTE:
            self._inside_quoteblock = True

    def leave_block(self, block, details):
        # print("LEAVE BLOCK", block.name, details)

        if block.value == md4c.BlockType.P:
            self._save_current_msgid()
            if not self._inside_liblock:
                self._save_current_line()
            self._inside_pblock = False
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = False
            self._inside_indented_codeblock = False
            if details['fence_char'] and details['fence_char'] != '\x00':
                self._current_line += '%s' % (details['fence_char']*3)
            self._save_current_line(times=2)
        elif block.value == md4c.BlockType.H:
            self._save_current_msgid()
            self._save_current_line()
            if self._inside_quoteblock:
                self._current_line += "> "
            self._save_current_line()
        elif block.value == md4c.BlockType.LI:
            self._save_current_msgid()
            self._inside_liblock = False
            self._save_current_line()
        elif block.value == md4c.BlockType.UL:
            self._ul_marks.pop()
            if self._inside_quoteblock:
                self._current_line += "> "
            if not self._ul_marks:
                self._save_current_line()
        elif block.value == md4c.BlockType.OL:
            self._current_ol_delimitier = None
            if self._inside_quoteblock:
                self._current_line += "> "
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
            self._current_line += "> "
        elif block.value == md4c.BlockType.TABLE:
            self._save_current_line()
        elif block.value == md4c.BlockType.DOC:
            pass

    def enter_span(self, span, details):
        # print("ENTER SPAN", span.name, details)

        try:
            self._current_msgid += self._enterspan_replacer[span.value]
        except KeyError:
            pass

        if span.value == md4c.SpanType.A:
            self._current_aspan_href = details["href"][0][1]
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
                self._current_msgid += "(%s" % self._current_aspan_href

                if details["title"]:
                    self._aimg_title_inside_current_msgid = True
                    self._current_msgid += ' "%s"' % polib.escape(
                        details["title"][0][1])
                self._current_msgid += ')'
                self._current_aspan_href = None
        elif span.value == md4c.SpanType.CODE:
            self._inside_codespan = False
            self._current_msgid += (
                self._codespan_backticks * self.code_end_string)
            self._codespan_backticks = None
        elif span.value == md4c.SpanType.IMG:
            self._current_msgid += polib.escape('![%s](%s' % (
                self._current_imgspan['text'], self._current_imgspan['src']
            ))
            if self._current_imgspan['title']:
                self._current_msgid += ' "%s"' % (
                    polib.escape(self._current_imgspan['title'])
                )
            self._current_msgid += ')'
            self._current_imgspan = {}

    def text(self, block, text):
        # print("TEXT", "'%s'" % text)
        if not self._inside_codeblock:
            if self._inside_liblock and text == "\n":
                text = ' '
            if self._current_imgspan:
                self._current_imgspan['text'] = text
                return
            elif self._inside_codespan:
                self._codespan_backticks = min_not_max_chars_in_a_row(
                    self.code_start_string,
                    text) - 1
                self._current_msgid = '%s%s%s' % (
                    self._current_msgid[:self._codespan_start_index],
                    self._codespan_backticks * self.code_start_string,
                    self._current_msgid[self._codespan_start_index:])
            elif text == self.italic_start_string:
                text = self.italic_start_string_escaped
            elif text == self.italic_end_string:
                text = self.italic_end_string_escaped
            elif text == self.code_start_string:
                text = self.code_start_string_escaped
            elif text == self.code_end_string:
                text = self.code_end_string_escaped

            if self._inside_pblock:
                text = text.replace("\n", " ")
            if self._current_aspan_href:
                if text == self._current_aspan_href:
                    # self-referenced link
                    self._current_aspan_href = None
            elif self._current_wikilink_target:
                if text != self._current_wikilink_target:
                    self._current_wikilink_target = '%s|%s' % (
                        self._current_wikilink_target, text)
                return
            self._current_msgid += polib.escape(text)
        else:
            if self._inside_indented_codeblock and text:
                if text == '\n':
                    return
                text = '    %s' % text
            self._current_line += text

    def translate(self, filepath_or_content, save=None):
        content = to_file_content_if_is_file(filepath_or_content)

        self.translations = {}
        for pofile in self.pofiles:
            for entry in pofile:
                self.translations[entry.msgid] = entry.msgstr

        parser = md4c.GenericParser(self.flags)
        parser.parse(content,
                     self.enter_block,
                     self.leave_block,
                     self.enter_span,
                     self.leave_span,
                     self.text)

        self.output = '\n'.join(self._outputlines)

        if save:
            with open(save, "w") as f:
                f.write(self.output)

        return self.output


def pofile_to_markdown(filepath_or_content, pofiles, ignore=[],
                       save=None, **kwargs):
    """Translate Markdown content or a file using pofiles for message replacing.

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

    Returns:
        str: Markdown output file with translated content.
    """
    return Po2Md(pofiles, ignore=ignore, **kwargs).translate(
        filepath_or_content, save=save
    )
