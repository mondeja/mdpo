import glob
import io
import os

import panflute as pf
import polib
import pypandoc

__version__ = '0.0.4'
__version_info__ = tuple([int(i) for i in __version__.split('.')])
__title__ = 'md2po'
__description__ = 'Extract the contents of a set of Markdown files' \
                + ' to one .po file.'

FORBIDDEN_CHARS = [
    '☒',
    '☐']
REPLACEMENT_CHARS = {
    '…': '...',
    '’': '\'',
}
FORBIDDEN_MSGIDS = [
    '.', '', ']`',
]


class Md2PoExtractor:
    def __init__(self, _glob, ignore=[], msgstr='', plaintext=True,
                 wrapwidth=78, forbidden_chars=FORBIDDEN_CHARS,
                 replacement_chars=REPLACEMENT_CHARS,
                 forbidden_msgids=FORBIDDEN_MSGIDS,
                 mark_not_found_as_absolete=True):
        self.ignore = ignore
        self.filepaths = self._ignore_files(glob.glob(_glob))

        self.pofile = None
        self.msgstr = ''
        self.msgids = []
        self._current_msgid = ''
        self.wrapwidth = wrapwidth
        self.mark_not_found_as_absolete = mark_not_found_as_absolete

        # If False, include some markup in response
        self.plaintext = plaintext

        self.forbidden_chars = forbidden_chars
        self.replacement_chars = replacement_chars
        self.forbidden_msgids = forbidden_msgids

    def _ignore_files(self, filepaths):
        response = []
        for filepath in filepaths:
            if os.path.basename(os.path.dirname(filepath)) in self.ignore:
                continue
            if os.path.basename(filepath) in self.ignore:
                continue
            response.append(filepath)
        response.sort()
        return response

    def _append_text_to_current_msgid(self, text):
        _text_to_append = ''
        for ch in text:
            if ch in self.forbidden_chars:
                continue
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

    def _extract_messages(self, elem, doc):
        # print(elem, '---', 'TYPE:', type(elem),
        #            '---', 'NEXT TYPE:', type(elem.next),
        #            '---', 'PARENT TYPE:', type(elem.parent))

        if isinstance(elem, (pf.Header, pf.Para)):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Link):
            if not self.plaintext:
                self._append_text_to_current_msgid(']`')
            if elem.title:
                self._save_msgid(elem.title)
            return
        elif isinstance(elem, pf.Plain) and \
                isinstance(elem.parent, pf.ListItem):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Emph):
            if not self.plaintext:
                self._append_text_to_current_msgid('*')
            return
        elif isinstance(elem, pf.Strong):
            if not self.plaintext:
                self._append_text_to_current_msgid('**')
            return
        elif isinstance(elem, pf.LineBreak):
            return self._save_current_msgid()
        elif isinstance(elem, pf.Image):
            if isinstance(elem.content, pf.ListContainer):
                _text = ''
                for container in elem.content:
                    if isinstance(container, pf.Space):
                        _text += ' '
                    else:
                        _text += container.text
                self._save_msgid(_text)

            if elem.title and elem.title != 'fig:':
                self._save_msgid(elem.title.lstrip(':fig'))
            return
        elif isinstance(elem, pf.Plain) and \
                isinstance(elem.parent, (pf.TableCell, pf.Definition)):
            return self._save_current_msgid()

        if isinstance(elem.parent, (pf.Para, pf.Header, pf.DefinitionItem)):
            if isinstance(elem, pf.Str):
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            elif isinstance(elem, pf.Code):
                if not self.plaintext:
                    self._append_text_to_current_msgid('`' + elem.text + '`')
                else:
                    self._append_text_to_current_msgid(elem.text)
            if isinstance(elem.next, pf.Link):
                if not self.plaintext:
                    self._append_text_to_current_msgid('`[')
            elif isinstance(elem.next, pf.Emph):
                if not self.plaintext:
                    self._append_text_to_current_msgid('*')
            elif not elem.next and isinstance(elem.parent, pf.DefinitionItem):
                self._save_current_msgid()

        elif isinstance(elem.parent, pf.Link):
            if isinstance(elem, pf.Str):
                if not self.plaintext and (not self._current_msgid or
                                           '`[' not in self._current_msgid):
                    self._append_text_to_current_msgid('`[')
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
        elif isinstance(elem.parent, pf.Plain):
            if isinstance(elem, pf.Str):
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            elif isinstance(elem, pf.Code):
                if not self.plaintext:
                    self._append_text_to_current_msgid('`' + elem.text + '`')
                else:
                    self._append_text_to_current_msgid(elem.text)

        elif isinstance(elem.parent, pf.Emph):
            if isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            else:
                if not self.plaintext and (not self._current_msgid or
                                           '*' not in self._current_msgid):
                    self._append_text_to_current_msgid('*')
                    if isinstance(elem.parent.parent, pf.Strong):
                        self._append_text_to_current_msgid('**')
                self._append_text_to_current_msgid(elem.text)
        elif isinstance(elem.parent, pf.Strong):
            if isinstance(elem, pf.Str):
                if not self.plaintext and (not self._current_msgid or
                                           '**' not in self._current_msgid):
                    self._append_text_to_current_msgid('**')
                self._append_text_to_current_msgid(elem.text)
            elif isinstance(elem, pf.Space):
                self._append_text_to_current_msgid(' ')
            elif isinstance(elem, pf.Code):
                if not self.plaintext and (not self._current_msgid or
                                           '**' not in self._current_msgid):
                    self._append_text_to_current_msgid('**')
                if not self.plaintext:
                    self._append_text_to_current_msgid('`' + elem.text + '`')
                else:
                    self._append_text_to_current_msgid(elem.text)

    def extract(self, po_filepath=None, save=False):
        _po_filepath = None
        if not po_filepath:
            po_filepath = ''
        else:
            _po_filepath = po_filepath
            if not os.path.exists(po_filepath):
                po_filepath = ''

        self.pofile = polib.pofile(po_filepath, wrapwidth=self.wrapwidth)

        for filepath in self.filepaths:
            data = pypandoc.convert_file(filepath, 'json')
            doc = pf.load(io.StringIO(data))
            doc.walk(self._extract_messages)

        if self.mark_not_found_as_absolete:
            for entry in self.pofile:
                if entry.msgid not in self.msgids:
                    entry.obsolete = True

        if save and _po_filepath:
            self.pofile.save(fpath=_po_filepath)
        return self.pofile


def markdown_to_pofile(_glob, ignore=[], msgstr='', po_filepath=None,
                       save=False, plaintext=True, wrapwidth=78,
                       mark_not_found_as_absolete=False):
    return Md2PoExtractor(
        _glob, ignore=ignore, msgstr=msgstr,
        plaintext=plaintext, wrapwidth=wrapwidth,
        mark_not_found_as_absolete=mark_not_found_as_absolete,
    ).extract(po_filepath=po_filepath, save=save)
