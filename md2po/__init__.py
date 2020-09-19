import glob
import os
import re

import md4c
import polib


__version__ = '0.1.10'
__version_info__ = tuple([int(i) for i in __version__.split('.')])
__title__ = 'md2po'
__description__ = ('Tiny utility like xgettext for msgid extracting from'
                   ' Markdown content.')

FORBIDDEN_MSGIDS = (' ', '\n')

DEFAULT_MD4C_FLAGS = ('MD_FLAG_COLLAPSEWHITESPACE|'
                      'MD_FLAG_TABLES|'
                      'MD_FLAG_STRIKETHROUGH|'
                      'MD_FLAG_TASKLIST|'
                      'MD_FLAG_LATEXMATHSPANS|'
                      'MD_FLAG_WIKILINKS')


def _build_escaped_string(char):
    return ''.join(["%s%s" % ('\\', c) for c in char])


def _parse_md4c_flags(flags):
    modes = {
        "strikethrough": False,
        "latexmathspans": False,
        "wikilinks": False,
        "underline": False,  # unactive by default
    }
    flags_string = flags.replace('+', '|').replace(' ', '')
    flags_list = []
    for flag in flags_string.split('|'):
        if not hasattr(md4c, flag):
            continue
        md4c_attr = getattr(md4c, flag)
        flags_list.append(md4c_attr)
        if md4c_attr == md4c.MD_FLAG_STRIKETHROUGH:
            modes["strikethrough"] = True
        elif md4c_attr == md4c.MD_FLAG_LATEXMATHSPANS:
            modes["latexmathspans"] = True
        elif md4c_attr == md4c.MD_FLAG_WIKILINKS:
            modes['wikilinks'] = True
        elif md4c_attr == md4c.MD_FLAG_UNDERLINE:
            modes['underline'] = True
    return (sum(flags_list), modes)


class Md2PoConverter:
    def __init__(self, *args, **kwargs):
        if not args or not args[0]:
            raise ValueError("You need to pass a glob or valid markdown"
                             " string as first argument.")
        _glob = glob.glob(args[0])
        if not _glob:
            # assumes it is content
            self.content = args[0]
        else:
            self.ignore = kwargs.get('ignore', [])
            self.filepaths = self._ignore_files(_glob)

        self.pofile = None
        self.msgstr = kwargs.get('msgstr', '')
        self.msgids = []
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

        self.wrapwidth = kwargs.get('wrapwidth', 78)

        self.mark_not_found_as_absolete = kwargs.get(
            'mark_not_found_as_absolete', False)

        self.flags, self.modes = _parse_md4c_flags(
            kwargs.get('flags', DEFAULT_MD4C_FLAGS))

        self.forbidden_msgids = kwargs.get('forbidden_msgids', None)
        if self.forbidden_msgids is None:
            self.forbidden_msgids = FORBIDDEN_MSGIDS

        self.plaintext = kwargs.get('plaintext', True)

        self.disable = False
        self.disable_next_line = False
        self.enable_next_line = False

        if not self.plaintext:
            self.bold_string = kwargs.get('bold_string', '**')
            self.bold_string_escaped = _build_escaped_string(
                self.bold_string)

            self.italic_string = kwargs.get('italic_string', '*')
            self.italic_string_escaped = _build_escaped_string(
                self.italic_string)

            self._bold_italic_context = False

            self.link_start_string = kwargs.get('link_start_string', '`[')
            self.link_end_string = kwargs.get('link_end_string', ']`')

            self.code_string = kwargs.get('code_string', '`')
            self.code_string_escaped = _build_escaped_string(
                self.code_string)

            self._enterspan_replacer = {
                md4c.SpanType.STRONG: self.bold_string,
                md4c.SpanType.EM: self.italic_string,
                md4c.SpanType.CODE: self.code_string,
                md4c.SpanType.A: self.link_start_string,
            }

            self._leavespan_replacer = {
                md4c.SpanType.STRONG: self.bold_string,
                md4c.SpanType.EM: self.italic_string,
                md4c.SpanType.CODE: self.code_string,
                md4c.SpanType.A: self.link_end_string,
            }

            if self.modes["strikethrough"]:
                self.strikethrough_string = kwargs.get(
                    'strikethrough_string', '~~')
                self._enterspan_replacer[md4c.SpanType.DEL] = \
                    self.strikethrough_string
                self._leavespan_replacer[md4c.SpanType.DEL] = \
                    self.strikethrough_string

            if self.modes['latexmathspans']:
                self.latexmath_string = kwargs.get(
                    'latexmath_string', '$')
                self._enterspan_replacer[md4c.SpanType.LATEXMATH] = \
                    self.latexmath_string
                self._leavespan_replacer[md4c.SpanType.LATEXMATH] = \
                    self.latexmath_string

                self.latexmathdisplay_string = kwargs.get(
                    'latexmathdisplay_string', '$$')
                self._enterspan_replacer[md4c.SpanType.LATEXMATH_DISPLAY] = \
                    self.latexmathdisplay_string
                self._leavespan_replacer[md4c.SpanType.LATEXMATH_DISPLAY] = \
                    self.latexmathdisplay_string

            if self.modes['wikilinks']:
                self._enterspan_replacer[md4c.SpanType.WIKILINK] = \
                    self.link_start_string
                self._leavespan_replacer[md4c.SpanType.WIKILINK] = \
                    self.link_end_string

            if self.modes['underline']:
                # underline text is standarized with double '_'
                self.underline_string = kwargs.get('underline_string', '__')
                self._enterspan_replacer[md4c.SpanType.U] = \
                    self.underline_string
                self._leavespan_replacer[md4c.SpanType.U] = \
                    self.underline_string
            # optimization to skip checking for ``self.modes['underline']``
            # inside spans
            self._inside_uspan = False

        self._inside_htmlblock = False
        self._inside_codeblock = False
        self._inside_codespan = False

    def _ignore_files(self, filepaths):
        response = []
        for filepath in filepaths:
            # ignore by filename
            if os.path.basename(filepath) in self.ignore:
                continue
            # ignore by dirname
            if os.path.basename(os.path.dirname(filepath)) in self.ignore:
                continue
            # ignore by filepath
            if filepath in self.ignore:
                continue
            # ignore by dirpath (relative or absolute)
            if (os.sep).join(filepath.split(os.sep)[:-1]) in self.ignore:
                continue
            response.append(filepath)
        response.sort()
        return response

    def _save_msgid(self, msgid, tcomment=None, msgctxt=None):
        if isinstance(msgid, str) and msgid not in self.forbidden_msgids:
            if polib.POEntry(msgid=msgid) not in self.pofile:
                entry = polib.POEntry(msgid=msgid, msgstr=self.msgstr,
                                      comment=tcomment,
                                      msgctxt=msgctxt)
                self.pofile.append(entry)
            self.msgids.append(msgid)

    def _save_current_msgid(self):
        if self._current_msgid and (
                (not self.disable_next_line and not self.disable) or
                self.enable_next_line):
            self._save_msgid(self._current_msgid.strip(' '),
                             tcomment=self._current_tcomment,
                             msgctxt=self._current_msgctxt)
        self.disable_next_line = False
        self.enable_next_line = False
        self._current_msgid = ''
        self._current_tcomment = None
        self._current_msgctxt = None

    def _process_command(self, text):
        command_search = re.search(
            r'<\!\-\-\s{0,1}md2po\-([a-z\-]+)\s{0,1}([\w\s]+)?\-\->', text)
        if command_search:
            command = command_search.group(1)
            if command == 'disable-next-line':
                self.disable_next_line = True
            elif command == 'disable':
                self.disable = True
            elif command == 'enable':
                self.disable = False
            elif command == 'enable-next-line':
                self.enable_next_line = True
            elif command == 'translator':
                comment = command_search.group(2)
                if comment is None:
                    raise ValueError('You need to specify a string for the'
                                     ' extracted comment with the command'
                                     ' \'md2po-translator\'.')
                self._current_tcomment = comment.strip(" ")
            elif command == 'context':
                comment = command_search.group(2)
                if comment is None:
                    raise ValueError('You need to specify a string for the'
                                     ' context with the command'
                                     ' \'md2po-context\'.')
                self._current_msgctxt = comment.strip(" ")
            elif command == 'include':
                comment = command_search.group(2)
                if comment is None:
                    raise ValueError('You need to specify a message for the'
                                     ' comment to include with the command'
                                     ' \'md2po-include\'.')
                self._current_msgid = comment.strip(" ")
                self._save_current_msgid()

    def enter_block(self, block, details):
        # print("ENTER BLOCK:", block.name)
        if block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = True
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = True

    def leave_block(self, block, details):
        # print("LEAVE BLOCK:", block.name)
        if block.value == md4c.BlockType.HTML:
            self._inside_htmlblock = False
        elif block.value == md4c.BlockType.CODE:
            self._inside_codeblock = False
        else:
            self._save_current_msgid()

    def enter_span(self, span, details):
        # print("ENTER SPAN:", span.name, details)
        if not self.plaintext:
            # underline spans for double '_' character enters two times
            if not self._inside_uspan:
                try:
                    self._current_msgid += self._enterspan_replacer[span.value]
                except KeyError:
                    pass

            if span.value == md4c.SpanType.CODE:
                self._inside_codespan = True
            if span.value == md4c.SpanType.U:
                self._inside_uspan = True

        if span.value in (md4c.SpanType.IMG, md4c.SpanType.A) and \
                details['title']:
            self._save_msgid(details['title'][0][1])

    def leave_span(self, span, details):
        # print("LEAVE SPAN:", span.name)
        if not self.plaintext:
            if not self._inside_uspan:
                try:
                    self._current_msgid += self._leavespan_replacer[span.value]
                except KeyError:
                    pass

            if span.value == md4c.SpanType.CODE:
                self._inside_codespan = False
            if span.value == md4c.SpanType.U:
                self._inside_uspan = False

    def text(self, block, text):
        # print("TEXT:", text)
        if not self._inside_htmlblock:
            if not self._inside_codeblock:
                if text == "\n":
                    text = ' '
                if not self.plaintext:
                    if self._inside_codespan:
                        text = re.sub(self.code_string,
                                      self.code_string_escaped, text)
                    elif text == self.italic_string:
                        text = self.italic_string_escaped
                    elif text == self.code_string:
                        text = self.code_string_escaped
                self._current_msgid += text
        else:
            self._process_command(text)

    def convert(self, po_filepath=None, save=False, encoding=None):
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
                self.disable_next_line = False
                self.disable = False

        if self.mark_not_found_as_absolete:
            for entry in self.pofile:
                if entry.msgid not in self.msgids:
                    entry.obsolete = True

        if save and _po_filepath:
            self.pofile.save(fpath=_po_filepath)
        return self.pofile


def markdown_to_pofile(glob_or_content, ignore=[], msgstr='',
                       po_filepath=None, save=False,
                       plaintext=True, wrapwidth=78,
                       mark_not_found_as_absolete=False,
                       flags=DEFAULT_MD4C_FLAGS,
                       forbidden_msgids=FORBIDDEN_MSGIDS,
                       encoding=None):
    """
    Extracts all the msgids from a string of Markdown content or a group
    of files.

    Args:
        glob_or_content (str): Glob path to Markdown files or a string
            with valid Markdown content.
        ignore (list): List of paths to files to ignore. Useful when
            a glob does not fit your requirements indicating the files
            to extract content from them. Also, filename or a dirname
            can be defined without indicate the full path.
        msgstr (str): Default message string for extracted msgids.
        po_filepath (str): File that will be used as :class:`polib.POFile`
            instance where to dump the new msgids and that will be used
            as source checking not found strings that will be marked as
            obsolete if is the case (see ``save`` and
            ``mark_not_found_as_absolete`` optional parameters).
        save (bool): Save the new content to the pofile indicated in the
            parameter ``po_filepath``.
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
        forbidden_msgids (list): Set of msgids that, if found, will not be
            included in output.
        encoding (bool): Resulting pofile encoding (autodetected by default).

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
        :class:`polib.POFile` instance with new msgids included.

    """
    return Md2PoConverter(
        glob_or_content, ignore=ignore, msgstr=msgstr,
        plaintext=plaintext, wrapwidth=wrapwidth,
        mark_not_found_as_absolete=mark_not_found_as_absolete,
        flags=flags, forbidden_msgids=forbidden_msgids,
    ).convert(po_filepath=po_filepath, save=save, encoding=encoding)
