"""Markdown files translator using PO files as reference."""

import md4c
import polib

from mdpo.command import (
    normalize_mdpo_command_aliases,
    parse_mdpo_html_command,
)
from mdpo.event import add_debug_events, parse_events_kwarg, raise_skip_event
from mdpo.io import save_file_checking_file_changed, to_file_content_if_is_file
from mdpo.md import MarkdownSpanWrapper, parse_link_references
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.po import (
    paths_or_globs_to_unique_pofiles,
    po_escaped_string,
    pofiles_to_unique_translations_dicts,
)
from mdpo.text import min_not_max_chars_in_a_row, parse_wrapwidth_argument


class Po2Md:
    """PO files to Markdown translator implementation.

    This class is where all the translation process is carried out.
    If you are executing custom translation events, you may want to
    read the documentation about the properties of this class to
    properly control the internal state of the parser.

    Example:
        If you want to translate all "Foo" messages as "Bar",
        regardless of the content of the actual translation,
        you could do something like:

        .. code-block:: python

           def transform_foo(self, block, text):
               if text == 'Foo':
                   self.current_msgid = 'Bar'  # self is Po2Md
                   return False

           pofile_to_markdown(
               'Foo',
               pofile_path,
               events={'text': transform_foo},
           )

    The public internal properties of this class are documented
    below:
    """
    __slots__ = {
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
        'bold_end_string',
        'italic_start_string',
        'italic_start_string_escaped',
        'italic_end_string',
        'italic_end_string_escaped',
        'code_start_string',
        'code_start_string_escaped',
        'code_end_string',
        'code_end_string_escaped',
        'wikilink_start_string',
        'wikilink_end_string',

        # Public class properties
        'current_msgid',
        'current_tcomment',
        'current_msgctxt',
        'disable',
        'disable_next_block',
        'enable_next_block',
        'current_line',
        'outputlines',

        '_saved_files_changed',

        '_enterspan_replacer',
        '_leavespan_replacer',

        '_inside_htmlblock',
        '_inside_codeblock',
        '_inside_indented_codeblock',
        '_inside_pblock',
        '_inside_liblock',
        '_inside_liblock_first_p',
        '_inside_hblock',
        '_inside_aspan',
        '_inside_codespan',
        '_codespan_start_index',
        '_codespan_backticks',
        '_codespan_inside_current_msgid',
        '_inside_quoteblock',
        '_current_aspan_ref_target',
        '_current_aspan_href',
        '_current_aspan_text',
        '_current_imgspan',
        '_current_thead_aligns',
        '_aimg_title_inside_current_msgid',
        '_ul_marks',
        '_ol_marks',
        '_current_list_type',
        '_current_wikilink_target',
        'link_references',
    }

    def __init__(self, pofiles, ignore=[], po_encoding=None, **kwargs):
        #: list(str): Paths to PO files to translate.
        self.pofiles = paths_or_globs_to_unique_pofiles(
            pofiles,
            ignore,
            po_encoding=po_encoding,
        )

        #: list(str): MD4C extensions used to parse the content.
        #: See all available in :doc:`/devref/mdpo/mdpo.md4c`.
        self.extensions = kwargs.get(
            'extensions',
            DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
        )

        #: dict: Custom events excuted during the parsing while
        #: translating content.
        self.events = (
            parse_events_kwarg(kwargs['events']) if 'events' in kwargs else {}
        )
        if kwargs.get('debug'):
            add_debug_events('po2md', self.events)

        #: str: The msgid being currently built for the next msgstr
        #: translation. Keep in mind that, if you are executing an event
        #: that will be followed by an span one (``enter_span`` or
        #: ``exit_span``), the content of the msgid will change before
        #: translate it.
        self.current_msgid = ''

        #: str: Translator comment that will be translated in the next
        #: msgid.
        self.current_tcomment = None

        #: str: Context message that will be translated in the next
        #: msgid.
        self.current_msgctxt = None

        #: str: Line currently being saved in the output.
        self.current_line = ''

        #: str: Lines currently added to the output.
        self.outputlines = []

        #: bool: Indicates if the translator is currently disabled,
        #: which happens after a ``<!-- mdpo-disable -->`` command
        #: is found, before any subsecuents ``<!-- mdpo-enable -->``
        #: commands.
        self.disable = False

        #: bool: Indicates if the next block will be translated.
        self.disable_next_block = False

        #: bool: Indicates if the next block will be translated
        #: when the translator is disabled
        self.enable_next_block = False

        #: list(:py:class:`polib.POEntry`): Disabled PO entries
        self.disabled_entries = []
        #: list(:py:class:`polib.POEntry`): Translated PO entries
        self.translated_entries = []

        self.translations = None
        self.translations_with_msgctxt = None

        self.command_aliases = (
            normalize_mdpo_command_aliases(kwargs['command_aliases'])
            if 'command_aliases' in kwargs else {}
        )

        self.wrapwidth = (
            # infinte gives some undesired rendering
            (
                2 ** 24 if kwargs['wrapwidth'] in [float('inf'), 0]
                else parse_wrapwidth_argument(kwargs['wrapwidth'])
            ) if 'wrapwidth' in kwargs else 80
        )

        self._saved_files_changed = (
            False if kwargs.get('_check_saved_files_changed') else None
        )

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

        self.code_start_string = kwargs.get('code_start_string', '`')[0]
        self.code_start_string_escaped = po_escaped_string(
            self.code_start_string,
        )

        self.code_end_string = kwargs.get('code_end_string', '`')[0]
        self.code_end_string_escaped = po_escaped_string(
            self.code_end_string,
        )

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

        self.wikilink_start_string = '[['
        self.wikilink_end_string = ']]'

        if 'wikilinks' in self.extensions:
            self.wikilink_start_string = kwargs.get(
                'link_end_string',
                self.wikilink_start_string,
            )
            self.wikilink_end_string = kwargs.get(
                'link_end_string',
                self.wikilink_end_string,
            )

            self._enterspan_replacer[md4c.SpanType.WIKILINK.value] = \
                self.wikilink_start_string
            self._leavespan_replacer[md4c.SpanType.WIKILINK.value] = \
                self.wikilink_end_string

        self._inside_htmlblock = False
        self._inside_codeblock = False
        self._inside_indented_codeblock = False
        self._inside_hblock = False
        self._inside_pblock = False
        self._inside_liblock = False
        # first li block paragraph (li block "title")
        self._inside_liblock_first_p = False

        self._inside_codespan = False
        self._codespan_start_index = None
        self._codespan_backticks = None
        self._codespan_inside_current_msgid = False

        self._inside_quoteblock = False

        self._inside_aspan = False
        self._current_aspan_ref_target = None
        self._current_aspan_href = None
        self._current_aspan_text = ''

        self.link_references = None
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
        # (second parameter is tasklist item or not)
        self._current_list_type = []

        self._current_wikilink_target = None

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

        if mdpo_command in (
            'mdpo-disable-next-block',
            'mdpo-disable-next-line',
        ):
            self.disable_next_block = True
        elif mdpo_command == 'mdpo-disable':
            self.disable = True
        elif mdpo_command == 'mdpo-enable':
            self.disable = False
        elif mdpo_command in (
            'mdpo-enable-next-block',
            'mdpo-enable-next-line',
        ):
            self.enable_next_block = True
        elif comment:
            if mdpo_command == 'mdpo-context':
                self.current_msgctxt = comment
            elif mdpo_command == 'mdpo-translator':
                self.current_tcomment = comment

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

    def _escape_translation(self, text):
        if self._aimg_title_inside_current_msgid:
            # escape '"' characters inside links and image titles
            text = polib.escape(text)
        return text

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
        # raise 'msgid' event
        if raise_skip_event(
            self.events,
            'msgid',
            self,
            self.current_msgid,
            None,
            self.current_msgctxt,
            self.current_tcomment,
            [],
        ):
            return

        if (not self.disable and not self.disable_next_block) or \
                self.enable_next_block:
            translation = self._translate_msgid(
                self.current_msgid,
                self.current_msgctxt,
                self.current_tcomment,
            )
        else:
            translation = self.current_msgid
            self.disabled_entries.append(
                polib.POEntry(
                    msgid=translation,
                    msgstr='',
                    msgctxt=self.current_msgctxt,
                    tcomment=self.current_tcomment,
                ),
            )

        if self._inside_indented_codeblock:
            new_translation = ''
            for line in translation.splitlines():
                new_translation += f'    {line}\n'
            translation = new_translation
        else:
            first_line_width_diff = 0
            if self._inside_liblock or self._inside_quoteblock:
                first_line_width_diff = -2
                if self._inside_liblock:
                    if self._current_list_type[-1][0] == 'ul':
                        if self._current_list_type[-1][-1][-1] is True:
                            first_line_width_diff = -6
                    else:
                        first_line_width_diff = -3

            if not self._inside_codeblock:
                indent = ''
                if len(self._current_list_type) > 1:
                    indent = '   ' * len(self._current_list_type)

                translation = MarkdownSpanWrapper(
                    width=self.wrapwidth,
                    first_line_width=self.wrapwidth + first_line_width_diff,
                    indent=indent,
                    md4c_extensions=self.extensions,
                    code_start_string=self.code_start_string,
                    code_end_string=self.code_end_string,
                    italic_start_string_escaped=(
                        self.italic_start_string_escaped
                    ),
                    italic_end_string_escaped=self.italic_end_string_escaped,
                    code_start_string_escaped=self.code_start_string_escaped,
                    code_end_string_escaped=self.code_end_string_escaped,
                    wikilink_start_string=self.wikilink_start_string,
                    wikilink_end_string=self.wikilink_end_string,
                ).wrap(translation)

                if self._inside_hblock or self._current_thead_aligns:
                    translation = translation.rstrip('\n')

        if translation.rstrip('\n'):
            self.current_line += translation

        self.current_msgid = ''
        self.current_msgctxt = None
        self.current_tcomment = None

        self.disable_next_block = False
        self.enable_next_block = False

        self._codespan_inside_current_msgid = False
        self._aimg_title_inside_current_msgid = False

    def _save_current_line(self):
        # strip all spaces according to unicodedata database ignoring newlines,
        # see https://docs.python.org/3/library/stdtypes.html#str.splitlines
        self.outputlines.append(self.current_line.rstrip(' \v\x0b\f\x0c'))
        self.current_line = ''

    def enter_block(self, block, details):
        # raise 'enter_block' event
        if raise_skip_event(
            self.events,
            'enter_block',
            self, block,
            details,
        ):
            return

        if (
            self._inside_quoteblock
            and (not self.current_line or self.current_line[0] != '>')
            and not self._current_thead_aligns
            and block not in {
                md4c.BlockType.TABLE, md4c.BlockType.THEAD, md4c.BlockType.TR,
            }
        ):
            self.current_line += '> '
        if block is md4c.BlockType.P:
            self._inside_pblock = True
        elif block is md4c.BlockType.CODE:
            self._inside_codeblock = True
            indent = ''

            if self._inside_liblock:
                self._save_current_msgid()
                if self.current_line:
                    self._save_current_line()
                indent += '   ' * len(self._current_list_type)

            if details['fence_char'] is not None:
                fence_chars = details['fence_char'] * 3
                self.current_line += f'{indent}{fence_chars}'
                if details['lang']:
                    self.current_line += details['lang'][0][1]
            else:
                self._inside_indented_codeblock = True

            if self.current_line:
                self._save_current_line()
        elif block is md4c.BlockType.H:
            self._inside_hblock = True
            hash_signs = '#' * details['level']
            self.current_line += f'{hash_signs} '
        elif block is md4c.BlockType.LI:
            if self._current_list_type[-1][0] == 'ol':
                # inside OL
                if len(self._ol_marks) > 1:
                    self._save_current_msgid()
                    if not self._ol_marks[-1][0]:
                        self._save_current_line()
                self._ol_marks[-1][0] += 1
                indent = '   ' * (len(self._current_list_type) - 1)
                self.current_line += f'{indent}1{self._ol_marks[-1][1]} '
                self._current_list_type[-1][-1].append(False)
            else:
                # inside UL
                indent = '   ' * (len(self._current_list_type) - 1)
                self.current_line += f'{indent}{self._ul_marks[-1]} '
                if details['is_task']:
                    mark = details['task_mark']
                    self.current_line += f'[{mark}] '
                self._current_list_type[-1][-1].append(details['is_task'])
            self._inside_liblock = True
            self._inside_liblock_first_p = True
        elif block is md4c.BlockType.UL:
            if self._current_list_type:
                self._save_current_msgid()
                self._save_current_line()
            self._current_list_type.append(['ul', []])
            self._ul_marks.append(details['mark'])
        elif block is md4c.BlockType.OL:
            self._current_list_type.append(['ol', []])
            self._ol_marks.append([0, details['mark_delimiter']])
        elif block is md4c.BlockType.HR:
            if self._current_list_type and not self.current_line:
                self._save_current_line()
            indent = (
                '   ' * len(self._current_list_type)
                if not self.current_line.startswith(('- ', '> - ')) else ''
            )
            self.current_line += f'{indent}***'
            self._save_current_line()
            if not self._inside_liblock:
                if self._inside_quoteblock:
                    self.current_line += f'{indent}>'
                self._save_current_line()
        elif block is md4c.BlockType.TR:
            self.current_line += '   ' * len(self._current_list_type)
            if self._inside_quoteblock and self._current_thead_aligns:
                self.current_line += '> '
        elif block is md4c.BlockType.TH:
            self.current_line += '| '
            self._current_thead_aligns.append(details['align'].value)
        elif block is md4c.BlockType.TD:
            self.current_line += '| '
        elif block is md4c.BlockType.QUOTE:
            if self._inside_liblock:
                self._save_current_msgid()
                self._save_current_line()
            self._inside_quoteblock = True
        elif block is md4c.BlockType.TABLE:
            if self._current_list_type and not self._inside_quoteblock:
                self._save_current_line()
        elif block is md4c.BlockType.HTML:
            self._inside_htmlblock = True

    def leave_block(self, block, details):
        # raise 'leave_block' event
        if raise_skip_event(
            self.events,
            'leave_block',
            self,
            block,
            details,
        ):
            return

        if block is md4c.BlockType.P:
            self._save_current_msgid()

            if self._inside_liblock:
                if self._inside_quoteblock:
                    indent = '   ' * len(self._current_list_type)
                    self.current_line = f'{indent}{self.current_line}'
                    self._save_current_line()
                else:
                    if self._inside_liblock_first_p:
                        self._inside_liblock_first_p = False
                    else:
                        indent = '   ' * len(self._current_list_type)
                        self.current_line = f'\n{indent}{self.current_line}'
                        self._save_current_line()
            else:
                self._save_current_line()

            self._inside_pblock = False
            if self._inside_quoteblock:
                self.current_line = '>'
                self._save_current_line()

        elif block is md4c.BlockType.CODE:
            self._save_current_msgid()
            self._inside_codeblock = False

            indent = ''
            if self._inside_liblock:
                indent += '   ' * len(self._current_list_type)
            self.current_line = self.current_line.rstrip('\n')
            self._save_current_line()
            if not self._inside_indented_codeblock:
                fence_chars = details['fence_char'] * 3
                self.current_line += f'{indent}{fence_chars}'

            self._save_current_line()
            if not self._inside_liblock:
                # prevent two newlines after indented code block
                if not self._inside_indented_codeblock:
                    self._save_current_line()
            self._inside_indented_codeblock = False
        elif block is md4c.BlockType.H:
            self._save_current_msgid()
            if self._inside_quoteblock:
                self._save_current_line()
                self.current_line += '> '
            else:
                self.current_line += '\n'
            self._save_current_line()
            if self._inside_quoteblock:
                self.current_line += '> '
            self._inside_hblock = False
        elif block is md4c.BlockType.LI:
            self._save_current_msgid()
            self._inside_liblock = False
            if self.current_line:
                self._save_current_line()
        elif block is md4c.BlockType.UL:
            self._ul_marks.pop()
            self._current_list_type.pop()
            if self._inside_quoteblock:
                self.current_line += '> '
            if not self._ul_marks and self.outputlines[-1].split('\n')[-1]:
                self._save_current_line()
        elif block is md4c.BlockType.OL:
            self._ol_marks.pop()
            self._current_list_type.pop()
            if self._inside_quoteblock:
                self.current_line += '> '
            if not self._ol_marks and self.outputlines[-1]:
                self._save_current_line()
        elif block in {md4c.BlockType.TH, md4c.BlockType.TD}:
            self._save_current_msgid()
            self.current_line += ' '
        elif block is md4c.BlockType.TR:
            self.current_line += '|'
            self._save_current_line()
        elif block is md4c.BlockType.THEAD:
            # build thead separator
            thead_separator = ''
            if self._inside_quoteblock:
                thead_separator += '> '
            for align in self._current_thead_aligns:
                if align == 0:
                    thead_separator += '| --- '
                elif align == 1:
                    thead_separator += '| :-- '
                elif align == 2:
                    thead_separator += '| :-: '
                else:
                    thead_separator += '| --: '

            indent = '   ' * len(self._current_list_type)
            self.current_line += f'{indent}{thead_separator}|'
            self._save_current_line()
        elif block is md4c.BlockType.QUOTE:
            if self.outputlines[-1] == '>':
                self.outputlines.pop()
            if not self._inside_liblock:
                self._save_current_line()
            self._inside_quoteblock = False
        elif block is md4c.BlockType.TABLE:
            if not self._inside_quoteblock and not self._current_list_type:
                self._save_current_line()
            self._current_thead_aligns = []
        elif block is md4c.BlockType.HTML:
            self._inside_htmlblock = False

    def enter_span(self, span, details):
        # raise 'enter_span' event
        if raise_skip_event(
            self.events,
            'enter_span',
            self,
            span,
            details,
        ):
            return

        if self._inside_aspan:  # span inside link text
            try:
                self._current_aspan_text += self._enterspan_replacer[
                    span.value
                ]
            except KeyError:
                pass
        else:
            try:
                self.current_msgid += self._enterspan_replacer[span.value]
            except KeyError:
                pass

        if span is md4c.SpanType.A:
            self._inside_aspan = True

            if self.link_references is None:
                self.link_references = parse_link_references(self.content)

            self._current_aspan_href = details['href'][0][1]
            self._current_aspan_ref_target = None

            if details['title']:
                current_aspan_title = details['title'][0][1]
                for target, href, title in self.link_references:
                    if (
                        href == self._current_aspan_href
                        and title == current_aspan_title
                    ):
                        self._current_aspan_ref_target = target
                        break
            else:
                for target, href, _ in self.link_references:
                    if href == self._current_aspan_href:
                        self._current_aspan_ref_target = target
                        break
        elif span is md4c.SpanType.CODE:
            self._inside_codespan = True
            self._codespan_start_index = len(self.current_msgid) - 1
            self._codespan_inside_current_msgid = True
        elif span is md4c.SpanType.IMG:
            if self.link_references is None:
                self.link_references = parse_link_references(self.content)

            self._current_imgspan['title'] = '' if not details['title'] \
                else details['title'][0][1]
            self._current_imgspan['src'] = details['src'][0][1]
            self._current_imgspan['text'] = ''
        elif span is md4c.SpanType.WIKILINK:
            self._current_wikilink_target = details['target'][0][1]

    def leave_span(self, span, details):
        # raise 'leave_span' event
        if raise_skip_event(
            self.events,
            'leave_span',
            self,
            span,
            details,
        ):
            return

        if span is md4c.SpanType.WIKILINK:
            self.current_msgid += polib.escape(self._current_wikilink_target)
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
                self.current_msgid += self._leavespan_replacer[span.value]
            except KeyError:
                pass

        if span is md4c.SpanType.A:
            if self._current_aspan_ref_target:  # referenced link
                self.current_msgid += f'[{self._current_aspan_text}]'
                if self._current_aspan_ref_target != self._current_aspan_text:
                    self.current_msgid += (
                        f'[{self._current_aspan_ref_target}]'
                    )
                self._current_aspan_ref_target = None
            else:
                if self._current_aspan_text == self._current_aspan_href:
                    # autolink vs link clash (see implementation notes)
                    self.current_msgid += f'<{self._current_aspan_text}'
                    if details['title']:
                        escaped_title = polib.escape(details['title'][0][1])
                        self.current_msgid += f' "{escaped_title}"'
                    self.current_msgid += '>'
                elif self._current_aspan_href:
                    self.current_msgid += (
                        f'[{self._current_aspan_text}]'
                        f'({self._current_aspan_href}'
                    )
                    if details['title']:
                        self._aimg_title_inside_current_msgid = True
                        escaped_title = polib.escape(details['title'][0][1])
                        self.current_msgid += f' "{escaped_title}"'
                    self.current_msgid += ')'
            self._current_aspan_href = None
            self._inside_aspan = False
            self._current_aspan_text = ''
        elif span is md4c.SpanType.CODE:
            self._inside_codespan = False
            self.current_msgid += (
                self._codespan_backticks * self.code_end_string
            )
            self._codespan_backticks = None
        elif span is md4c.SpanType.IMG:
            referenced_target, imgspan_title = (None, None)
            imgspan_src = details['src'][0][1]
            if details['title']:
                imgspan_title = polib.escape(details['title'][0][1])
                for target, href, title in self.link_references:
                    if href == imgspan_src and title == imgspan_title:
                        referenced_target = target
                        break
            else:
                for target, href, _ in self.link_references:
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
                    img_markup += f' "{imgspan_title}"'
                img_markup += ')'

            if self._inside_aspan:
                self._current_aspan_text += img_markup
            else:
                self.current_msgid += img_markup

            self._current_imgspan = {}

    def text(self, block, text):
        # raise 'text' event
        if raise_skip_event(
            self.events,
            'text',
            self,
            block,
            text,
        ):
            return

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
                    self.current_msgid = (
                        f'{self.current_msgid[:self._codespan_start_index]}'
                        f'{self._codespan_backticks * self.code_start_string}'
                        f'{self.current_msgid[self._codespan_start_index:]}'
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
                        self._current_wikilink_target = (
                            f'{self._current_wikilink_target}|{text}'
                        )
                    return
                self.current_msgid += text
            else:
                if self._inside_liblock:
                    indent = '   ' * len(self._current_list_type)
                    if self.current_line[:len(indent) + 1] != indent:
                        self.current_line += indent
                self.current_msgid += text
        else:
            self._process_command(text)

    def _append_link_references(self):
        if self.link_references:
            self.disable_next_block = False
            self.disable = False

            # 'link_reference' event
            pre_events = self.events.get('link_reference')

            added_references = []  # don't repeat references
            for target, href, title in self.link_references:
                if pre_events:
                    skip = False
                    for event in pre_events:
                        if event(self, target, href, title) is False:
                            skip = True
                    if skip:
                        continue
                title_part = f' "{title}"' if title else ''
                href_title = f' {href}{title_part}'
                if href_title in added_references:
                    continue

                msgid = f'[{target}]:{href_title}'
                self.outputlines.append(
                    self._translate_msgid(msgid, None, None),
                )
                added_references.append(href_title)
            self.outputlines.append('')

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
        self._append_link_references()  # add link references to the end

        self.disable_next_block = False
        self.disable = False
        self.enable_next_block = False
        self.link_references = None

        self.output = '\n'.join(self.outputlines)

        if save:
            if self._saved_files_changed is False:
                self._saved_files_changed = save_file_checking_file_changed(
                    save,
                    self.output,
                    encoding=md_encoding,
                )
            else:
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
    debug=False,
    **kwargs,
):
    r"""Translate Markdown content or file using PO files as reference.

    This implementation reproduces the same valid Markdown output, given the
    provided AST, with replaced translations, but doesn't rebuilds the same
    input format as Markdown is just a subset of HTML.

    Args:
        filepath_or_content (str): Markdown filepath or content to translate.
        pofiles (str, list) Glob or list of globs matching a set of PO files
            from where to extract messages to make the replacements translating
            strings.
        ignore (list): Paths of PO files to ignore. Useful when a glob does not
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
            process that can be used to customize the output. Takes list of
            functions as values. If one of these functions returns ``False``,
            that part of the translation process is skipped by ``po2md``.
            Available events are the next:

            * ``enter_block(self, block, details)``: Executed when the parsing
              of a Markdown block starts.
            * ``leave_block(self, block, details)``: Executed when the parsing
              of a Markdown block ends.
            * ``enter_span(self, span, details)``: Executed when the parsing of
              a Markdown span starts.
            * ``leave_span(self, span, details)``: Executed when the parsing of
              a Markdown span ends.
            * ``text(self, block, text)``: Executed when the parsing of text
              starts.
            * ``command(self, mdpo_command, comment, original command)``:
              Executed when a mdpo HTML command is found.
            * ``msgid(self, msgid, msgstr, msgctxt, tcomment, flags)``:
              Executed when a msgid is going to be replaced.
            * ``link_reference(self, target, href, title)``: Executed when each
              reference link is being written in the output (at the end of the
              translation process).

            You can also define the location of these functions by strings
            with the syntax ``path/to/file.py::function_name``.
        debug (bool): Add events displaying all parsed elements in the
            translation process.

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
        debug=debug,
        **kwargs,
    ).translate(
        filepath_or_content,
        save=save,
        md_encoding=md_encoding,
    )
