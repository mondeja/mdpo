import glob
import io
import os

import panflute as pf
import polib
import pypandoc

__version__ = '0.0.18'
__version_info__ = tuple([int(i) for i in __version__.split('.')])
__title__ = 'md2po'
__description__ = 'Extract the contents of a set of Markdown files' \
                + ' to one .po file.'

REPLACEMENT_CHARS = {'’': '\''}
FORBIDDEN_MSGIDS = ('', ' ', '\n')


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
        self.wrapwidth = kwargs.get('wrapwidth', 78)
        self.mark_not_found_as_absolete = kwargs.get(
            'mark_not_found_as_absolete', False)

        self.replacement_chars = kwargs.get('replacement_chars', None)
        if self.replacement_chars is None:
            self.replacement_chars = REPLACEMENT_CHARS
        self.forbidden_msgids = kwargs.get('forbidden_msgids', None)
        if self.forbidden_msgids is None:
            self.forbidden_msgids = FORBIDDEN_MSGIDS

        self.plaintext = kwargs.get('plaintext', True)

        if not self.plaintext:
            self.bold_string = kwargs.get('bold_string', '**')
            self.bold_string_replacer = ''.join([
                "\\%s" % c for c in self.bold_string])

            self.italic_string = kwargs.get('italic_string', '*')
            self.italic_string_replacer = ''.join([
                "\\%s" % c for c in self.italic_string])

            self._current_italic_chars = 0
            self._current_bold_chars = 0

            self.link_start_string = kwargs.get('link_start_string', '`[')
            self.link_end_string = kwargs.get('link_end_string', ']`')

            self.code_string = kwargs.get('code_string', '`')
            self.code_string_replacer = ''.join([
                "\\%s" % c for c in self.code_string])

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

    def _append_text_to_current_msgid(self, text):
        _text_to_append = ''
        for ch in text:
            if ch in self.replacement_chars:
                ch = self.replacement_chars[ch]
            _text_to_append += ch
        self._current_msgid += _text_to_append

    def _save_msgid(self, msgid):
        if isinstance(msgid, str) and msgid not in self.forbidden_msgids:
            if polib.POEntry(msgid=msgid) not in self.pofile:
                self.pofile.append(
                    polib.POEntry(msgid=msgid, msgstr=self.msgstr))
            self.msgids.append(msgid)

    def _save_current_msgid(self):
        self._save_msgid(self._current_msgid.strip(' '))
        self._current_msgid = ''
        self._current_italic_chars = 0
        self._current_bold_chars = 0

    def _extract_msgids(self, elem, doc):
        # print('\n%s | TYPE: %s\nNEXT TYPE: %s | PARENT TYPE %s' % (
        #       elem, type(elem), type(elem.next), type(elem.parent)))

        if isinstance(elem, (pf.Header, pf.Para)):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Link):
            if not self.plaintext:
                self._append_text_to_current_msgid(self.link_end_string)
            if elem.title:
                self._save_msgid(elem.title)
            return
        elif isinstance(elem, pf.Plain) and \
                isinstance(elem.parent, pf.ListItem):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Emph):
            if not self.plaintext:
                self._append_text_to_current_msgid(self.italic_string)
            return
        elif isinstance(elem, pf.Strong):
            if not self.plaintext:
                self._append_text_to_current_msgid(self.bold_string)
            return
        elif isinstance(elem, pf.LineBreak):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Image):
            if isinstance(elem.content, pf.ListContainer):
                _text = ''
                for container in elem.content:
                    _text += ' ' if isinstance(container, pf.Space) else \
                        container.text
                self._save_msgid(_text)
            if elem.title and elem.title != 'fig:':
                self._save_msgid(elem.title.lstrip(':fig'))
            return
        elif isinstance(elem, pf.Plain) and \
                isinstance(elem.parent, (pf.TableCell, pf.Definition)):
            return self._save_current_msgid()

        if isinstance(elem.parent, (pf.Para, pf.Header,
                                    pf.DefinitionItem, pf.Plain)):
            if isinstance(elem, pf.Str):
                if not self.plaintext:
                    if self.bold_string in elem.text:
                        self._current_bold_chars += 1
                        self._append_text_to_current_msgid(
                            elem.text.replace(self.bold_string,
                                              self.bold_string_replacer))
                    elif self.italic_string in elem.text:
                        self._current_italic_chars += 1
                        self._append_text_to_current_msgid(
                            elem.text.replace(self.italic_string,
                                              self.italic_string_replacer))
                    else:
                        self._append_text_to_current_msgid(elem.text)
                else:
                    self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            elif isinstance(elem, pf.Code):
                if not self.plaintext:
                    self._append_text_to_current_msgid(
                        self.code_string +
                        elem.text.replace(self.code_string,
                                          self.code_string_replacer) +
                        self.code_string)
                else:
                    self._append_text_to_current_msgid(elem.text)
            if isinstance(elem.next, pf.Link):
                if not self.plaintext:
                    self._append_text_to_current_msgid(self.link_start_string)
            elif isinstance(elem.next, pf.Emph):
                if not self.plaintext:
                    self._append_text_to_current_msgid(self.italic_string)
            elif not elem.next and isinstance(elem.parent, pf.DefinitionItem):
                self._save_current_msgid()

        elif isinstance(elem.parent, pf.Link):
            if isinstance(elem, pf.Str):
                if not self.plaintext and (
                        not self._current_msgid or
                        self.link_start_string not in self._current_msgid):
                    self._append_text_to_current_msgid(self.link_start_string)
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
        elif isinstance(elem.parent, pf.Emph):
            if isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            else:
                if not self.plaintext and (
                        self._current_msgid.count(self.italic_string) == 0 or (
                        self._current_msgid.count(self.italic_string) -
                        self._current_italic_chars) % 2 == 0):
                    self._append_text_to_current_msgid(self.italic_string)
                    if isinstance(elem.parent.parent, pf.Strong):
                        self._append_text_to_current_msgid(self.bold_string)
                self._append_text_to_current_msgid(elem.text)
        elif isinstance(elem.parent, pf.Strong):
            if isinstance(elem, pf.Str):
                if not self.plaintext and (
                        self._current_msgid.count(self.bold_string) == 0 or (
                        self._current_msgid.count(self.bold_string) -
                        self._current_bold_chars) % 2 == 0):
                    self._append_text_to_current_msgid(self.bold_string)
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            elif isinstance(elem, pf.Code):
                if not self.plaintext and (
                        self._current_msgid.count(self.bold_string) == 0 or (
                        self._current_msgid.count(self.bold_string) -
                        self._current_bold_chars) % 2 == 0):
                    self._append_text_to_current_msgid(self.bold_string)
                if not self.plaintext:
                    self._append_text_to_current_msgid(
                        self.code_string +
                        elem.text.replace(self.code_string,
                                          self.code_string_replacer) +
                        self.code_string)
                else:
                    self._append_text_to_current_msgid(elem.text)

    def convert(self, po_filepath=None, save=False):
        _po_filepath = None
        if not po_filepath:
            po_filepath = ''
        else:
            _po_filepath = po_filepath
            if not os.path.exists(po_filepath):
                po_filepath = ''

        self.pofile = polib.pofile(po_filepath, wrapwidth=self.wrapwidth)

        def _load_walk(data):
            doc = pf.load(io.StringIO(data))
            doc.walk(self._extract_msgids)

        if hasattr(self, 'content'):
            data = pypandoc.convert_text(self.content, format='md', to='json')
            _load_walk(data)
        else:
            for filepath in self.filepaths:
                data = pypandoc.convert_file(filepath, 'json')
                _load_walk(data)

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
                       replacement_chars=REPLACEMENT_CHARS,
                       forbidden_msgids=FORBIDDEN_MSGIDS,
                       bold_string='**', italic_string='*', code_string='`',
                       link_start_string='`[', link_end_string=']`'):
    """
    Extracts all the msgids from a string of Markdown content or a group
    of files and returns a :class:`polib.POFile` instance.

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
        replacement_chars (dict) Pairs of substitution characters that will
            be replaced each key with their value in the output.
        forbidden_msgids (list) Set of msgids that, if found, will not be
            included in output.
        bold_string (str) String that represents the markup character/s at
            the beginning and the end of a chunk of bold text.
        italic_string (str) String that represents the markup character/s at
            the beginning and the end of an italic text.
        code_string (str) String that represents the markup character/s at
            the beginning and the end of an inline piece of code.
        link_start_string (str) String that represents the markup character/s
            at the beginning of a link.
        link_end_string (str) String that represents the markup character/s
            at the end of a link.

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
        replacement_chars=replacement_chars,
        forbidden_msgids=forbidden_msgids,
        bold_string=bold_string, italic_string=italic_string,
        link_start_string=link_start_string,
        link_end_string=link_end_string, code_string=code_string
    ).convert(po_filepath=po_filepath, save=save)
