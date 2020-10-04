"""Markdown to pofiles extractor according to mdpo specification."""

import os

import md4c
import polib

from mdpo.command import search_html_command
from mdpo.io import filter_paths, to_glob_or_content
from mdpo.md4c import DEFAULT_MD4C_FLAGS, parse_md4c_flags_string
from mdpo.po import build_po_escaped_string
from mdpo.text import min_not_max_chars_in_a_row


class Md2Po:
    def __init__(self, glob_or_content, **kwargs):
        is_glob, glob_or_content = to_glob_or_content(glob_or_content)
        if is_glob:
            self.filepaths = filter_paths(
                glob_or_content,
                ignore_paths=kwargs.get('ignore', []))
        else:
            self.content = glob_or_content

        self.pofile = None
        self.msgstr = kwargs.get('msgstr', '')
        self.msgids = []
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

        self.wrapwidth = kwargs.get('wrapwidth', 78)

        self.mark_not_found_as_absolete = kwargs.get(
            'mark_not_found_as_absolete', True)

        self.flags, self.modes = parse_md4c_flags_string(
            kwargs.get('flags', DEFAULT_MD4C_FLAGS))

        self.plaintext = kwargs.get('plaintext', False)

        self._disable = False
        self._disable_next_line = False
        self._enable_next_line = False

        self._include_xheaders = False

        if not self.plaintext:
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

            # codespans are built by a indetermined number of 'x' characters
            # so we take only the first
            self.code_start_string = kwargs.get('code_start_string', '`')[0]
            self.code_start_string_escaped = build_po_escaped_string(
                self.code_start_string)

            self.code_end_string = kwargs.get('code_end_string', '`')[0]
            self.code_end_string_escaped = build_po_escaped_string(
                self.code_end_string)

            self.link_start_string = kwargs.get('link_start_string', '[')
            self.link_end_string = kwargs.get('link_end_string', ']')

            self._include_xheaders = kwargs.get("xheaders", False)
            if self._include_xheaders:
                self.xheaders = {
                    "x-mdpo-bold-start": self.bold_start_string,
                    "x-mdpo-bold-end": self.bold_end_string,
                    "x-mdpo-italic-start": self.italic_start_string,
                    "x-mdpo-italic-end": self.italic_end_string,
                    "x-mdpo-code-start": self.code_start_string,
                    "x-mdpo-code-end": self.code_end_string,
                    "x-mdpo-link-start": self.link_start_string,
                    "x-mdpo-link-end": self.link_end_string,
                }

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

            if self.modes["strikethrough"]:
                self.strikethrough_start_string = kwargs.get(
                    'strikethrough_start_string', '~~')
                self._enterspan_replacer[md4c.SpanType.DEL] = \
                    self.strikethrough_start_string

                self.strikethrough_end_string = kwargs.get(
                    'strikethrough_end_string', '~~')
                self._leavespan_replacer[md4c.SpanType.DEL] = \
                    self.strikethrough_end_string

                if self._include_xheaders:
                    self.xheaders.update({
                        "x-mdpo-strikethrough-start":
                            self.strikethrough_start_string,
                        "x-mdpo-strikethrough-end":
                            self.strikethrough_end_string,
                    })

            if self.modes['latexmathspans']:
                self.latexmath_start_string = kwargs.get(
                    'latexmath_start_string', '$')
                self._enterspan_replacer[md4c.SpanType.LATEXMATH] = \
                    self.latexmath_start_string

                self.latexmath_end_string = kwargs.get(
                    'latexmath_end_string', '$')
                self._leavespan_replacer[md4c.SpanType.LATEXMATH] = \
                    self.latexmath_end_string

                self.latexmathdisplay_start_string = kwargs.get(
                    'latexmathdisplay_start_string', '$$')
                self._enterspan_replacer[md4c.SpanType.LATEXMATH_DISPLAY] = \
                    self.latexmathdisplay_start_string

                self.latexmathdisplay_end_string = kwargs.get(
                    'latexmathdisplay_end_string', '$$')
                self._leavespan_replacer[md4c.SpanType.LATEXMATH_DISPLAY] = \
                    self.latexmathdisplay_end_string

                if self._include_xheaders:
                    self.xheaders.update({
                        "x-mdpo-latexmath-start": self.latexmath_start_string,
                        "x-mdpo-latexmath-end": self.latexmath_end_string,
                        "x-mdpo-latexmathdisplay-start":
                            self.latexmathdisplay_start_string,
                        "x-mdpo-latexmathdisplay-end":
                            self.latexmathdisplay_end_string,
                    })

            if self.modes['wikilinks']:
                self.wikilink_start_string = kwargs.get(
                    'wikilink_start_string', '[[')
                self.wikilink_end_string = kwargs.get(
                    'wikilink_end_string', ']]')

                self._enterspan_replacer[md4c.SpanType.WIKILINK] = \
                    self.wikilink_start_string
                self._leavespan_replacer[md4c.SpanType.WIKILINK] = \
                    self.wikilink_end_string

                if self._include_xheaders:
                    self.xheaders.update({
                        "x-mdpo-wikilink-start": self.wikilink_start_string,
                        "x-mdpo-wikilink-end": self.wikilink_end_string,
                    })

            if self.modes['underline']:
                # underline text is standarized with double '_'
                self.underline_start_string = kwargs.get(
                    'underline_start_string', '__')
                self._enterspan_replacer[md4c.SpanType.U] = \
                    self.underline_start_string

                self.underline_end_string = kwargs.get(
                    'underline_end_string', '__')
                self._leavespan_replacer[md4c.SpanType.U] = \
                    self.underline_end_string

                if self._include_xheaders:
                    self.xheaders.update({
                        "x-mdpo-underline-start": self.underline_start_string,
                        "x-mdpo-underline-end": self.underline_end_string,
                    })

            # optimization to skip checking for ``self.modes['underline']``
            # inside spans
            self._inside_uspan = False

        self._inside_htmlblock = False
        self._inside_codeblock = False
        self._inside_pblock = False
        self._inside_liblock = False

        self._inside_codespan = False
        self._codespan_start_index = None
        self._codespan_backticks = None

        self._current_aspan_href = None
        self._current_wikilink_target = None
        self._current_imgspan = {}

        # ULs deep
        self._uls_deep = 0

    def _save_msgid(self, msgid, tcomment=None, msgctxt=None):
        if polib.POEntry(msgid=msgid) not in self.pofile:
            entry = polib.POEntry(msgid=msgid, msgstr=self.msgstr,
                                  comment=tcomment,
                                  msgctxt=msgctxt)
            self.pofile.append(entry)
        self.msgids.append(msgid)

    def _save_current_msgid(self):
        if self._current_msgid and ((not self._disable_next_line and
                                     not self._disable) or
                                    self._enable_next_line):
            self._save_msgid(self._current_msgid,
                             tcomment=self._current_tcomment,
                             msgctxt=self._current_msgctxt)
        self._disable_next_line = False
        self._enable_next_line = False
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

    def _process_command(self, text):
        command, comment = search_html_command(text)
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
        elif command == 'translator':
            if not comment:
                raise ValueError('You need to specify a string for the'
                                 ' extracted comment with the command'
                                 ' \'mdpo-translator\'.')
            self._current_tcomment = comment.strip(" ")
        elif command == 'context':
            if not comment:
                raise ValueError('You need to specify a string for the'
                                 ' context with the command \'mdpo-context\'.')
            self._current_msgctxt = comment.strip(" ")
        elif command == 'include':
            if not comment:
                raise ValueError('You need to specify a message for the'
                                 ' comment to include with the command'
                                 ' \'mdpo-include\'.')
            self._current_msgid = comment.strip(" ")
            self._save_current_msgid()

    def enter_block(self, block, details):
        # print("ENTER BLOCK:", block.name)
        if block.value == md4c.BlockType.P:
            self._inside_pblock = True
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = True
        elif block.value == md4c.BlockType.LI:
            self._inside_liblock = True
        elif block.value == md4c.BlockType.UL:
            self._uls_deep += 1
            if self._uls_deep > 1:
                # changing UL deeep
                self._save_current_msgid()
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = True

    def leave_block(self, block, details):
        # print("LEAVE BLOCK:", block.name)
        if block.value == md4c.BlockType.CODE:
            self._inside_codeblock = False
        elif block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = False
        else:
            if block.value == md4c.BlockType.P:
                self._inside_pblock = False
            elif block.value == md4c.BlockType.LI:
                self._inside_liblock = True
            elif block.value == md4c.BlockType.UL:
                self._uls_deep -= 1
            self._save_current_msgid()

    def enter_span(self, span, details, *args):
        # print("ENTER SPAN:", span.name, details)
        if not self.plaintext:
            # underline spans for double '_' character enters two times
            if not self._inside_uspan:
                try:
                    self._current_msgid += self._enterspan_replacer[span.value]
                except KeyError:
                    pass

            if span.value == md4c.SpanType.A:
                self._current_aspan_href = details["href"][0][1]
            elif span.value == md4c.SpanType.CODE:
                self._inside_codespan = True

                # entering a code span, literal backticks encountered inside
                # will be escaped
                #
                # save the index char of the opening backtick
                self._codespan_start_index = len(self._current_msgid) - 1
            elif span.value == md4c.SpanType.IMG:
                self._current_imgspan['src'] = details['src'][0][1]
                self._current_imgspan['title'] = '' if not details['title'] \
                    else details['title'][0][1]
                self._current_imgspan['text'] = ''
            elif span.value == md4c.SpanType.U:
                self._inside_uspan = True
            elif span.value == md4c.SpanType.WIKILINK:
                self._current_wikilink_target = details['target'][0][1]
        else:
            if span.value in (md4c.SpanType.IMG, md4c.SpanType.A) and \
                    details['title']:
                self._save_msgid(details['title'][0][1])

    def leave_span(self, span, details):
        # print("LEAVE SPAN:", span.name)
        if not self.plaintext:
            if not self._inside_uspan:
                if span.value == md4c.SpanType.WIKILINK:
                    self._current_msgid += self._current_wikilink_target
                    self._current_wikilink_target = None

                try:
                    self._current_msgid += self._leavespan_replacer[span.value]
                except KeyError:
                    pass

            if span.value == md4c.SpanType.A:
                if self._current_aspan_href:
                    self._current_msgid += "(%s%s)" % (
                        self._current_aspan_href,
                        "" if not details['title'] else ' "%s"' % (
                            details['title'][0][1])
                    )
                    self._current_aspan_href = None
            elif span.value == md4c.SpanType.CODE:
                self._inside_codespan = False
                self._codespan_start_index = None
                # add backticks at the end for escape internal backticks
                self._current_msgid += (
                    self._codespan_backticks * self.code_end_string)
                self._codespan_backticks = None
            elif span.value == md4c.SpanType.IMG:
                self._current_msgid += '![%s](%s' % (
                    self._current_imgspan['text'], self._current_imgspan['src']
                )
                if self._current_imgspan['title']:
                    self._current_msgid += ' "%s"' % (
                        self._current_imgspan['title'])
                self._current_msgid += ')'
                self._current_imgspan = {}
            elif span.value == md4c.SpanType.U:
                self._inside_uspan = False

    def text(self, block, text):
        # print("TEXT:", text)
        if not self._inside_htmlblock:
            if not self._inside_codeblock:
                if self._inside_liblock and text == "\n":
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
                if self._current_wikilink_target:
                    if text != self._current_wikilink_target:
                        # not self-referenced wikilink
                        self._current_wikilink_target = '%s|%s' % (
                            self._current_wikilink_target,
                            text)
                    return
                self._current_msgid += text
        else:
            self._process_command(text)

    def extract(self, po_filepath=None, save=False, mo_filepath=None,
                encoding=None):
        _po_filepath = None
        if not po_filepath:
            po_filepath = ''
        else:
            _po_filepath = po_filepath
            if not os.path.exists(po_filepath):
                po_filepath = ''

        pofile_kwargs = (dict(autodetect_encoding=False, encoding=encoding) if
                         encoding else {})
        self.pofile = polib.pofile(po_filepath, wrapwidth=self.wrapwidth,
                                   **pofile_kwargs)

        parser = md4c.GenericParser(self.flags)

        def _parse(content):
            parser.parse(content,
                         self.enter_block,
                         self.leave_block,
                         self.enter_span,
                         self.leave_span,
                         self.text)

        if hasattr(self, 'content'):
            _parse(self.content)
        else:
            for filepath in self.filepaths:
                with open(filepath, "r") as f:
                    content = f.read()
                _parse(content)
                self._disable_next_line = False
                self._disable = False
                self._enable_next_line = False

        if self.mark_not_found_as_absolete:
            for entry in self.pofile:
                if entry.msgid not in self.msgids:
                    entry.obsolete = True

        if self._include_xheaders:
            self.pofile.metadata.update(self.xheaders)

        if save and _po_filepath:
            self.pofile.save(fpath=_po_filepath)
        if mo_filepath:
            self.pofile.save_as_mofile(mo_filepath)
        return self.pofile


def markdown_to_pofile(glob_or_content, ignore=[], msgstr='',
                       po_filepath=None, save=False, mo_filepath=None,
                       plaintext=False, wrapwidth=78,
                       mark_not_found_as_absolete=True,
                       flags=DEFAULT_MD4C_FLAGS, encoding=None,
                       xheaders=False, **kwargs):
    """
    Extracts all the msgids from a string of Markdown content or a group
    of files.

    Args:
        glob_or_content (str): Glob path to Markdown files or a string
            with valid Markdown content.
        ignore (list): Paths of files to ignore. Useful when a glob does not
            fit your requirements indicating the files to extract content.
            Also, filename or a dirname can be defined without indicate the
            full path.
        msgstr (str): Default message string for extracted msgids.
        po_filepath (str): File that will be used as :class:`polib.POFile`
            instance where to dump the new msgids and that will be used
            as source checking not found strings that will be marked as
            obsolete if is the case (see ``save`` and
            ``mark_not_found_as_absolete`` optional parameters).
        save (bool): Save the new content to the pofile indicated in the
            parameter ``po_filepath``.
        mo_filepath (str): The resulting pofile will be compiled to a mofile
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
            parameter. Only useful when the ``-w`` option was passed
            to xgettext.
        mark_not_found_as_absolete (bool): The strings extracted from markdown
            that will not be found inside the provided pofile will be marked
            as obsolete.
        flags (str): md4c extensions used to parse markdown content, separated
            by ``|`` or ``+`` characters. You can see all available at
            `md4c repository <https://github.com/mity/md4c#markdown-
            extensions>`_.
        encoding (bool): Resulting pofile encoding (autodetected by default).
        xheaders (bool): Indicates if the resulting pofile will have mdpo
            x-headers included. These only can be included if the parameter
            ``plaintext`` is ``False``.

    Examples:
        >>> content = 'Some text with `inline code`'
        >>> entries = markdown_to_pofile(content)
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with inline code': ''}
        >>> entries = markdown_to_pofile(content, plaintext=False)
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with `inline code`': ''}
        >>> entries = markdown_to_pofile(content, msgstr='Default message')
        >>> {e.msgid: e.msgstr for e in entries}
        {'Some text with inline code': 'Default message'}

    Returns:
        :class:`polib.POFile`:: Pofile instance with new msgids included.

    """
    return Md2Po(
        glob_or_content, ignore=ignore, msgstr=msgstr,
        plaintext=plaintext, wrapwidth=wrapwidth,
        mark_not_found_as_absolete=mark_not_found_as_absolete,
        flags=flags, xheaders=xheaders, **kwargs
    ).extract(
        po_filepath=po_filepath, save=save,
        mo_filepath=mo_filepath, encoding=encoding
    )
