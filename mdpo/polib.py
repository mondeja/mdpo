"""Workaround for polib issues until polib is updated. See
https://github.com/izimobil/polib/pulls for details.
"""

from polib import POEntry


def _poentry__cmp__(self, other, compare_obsolete=True):
    """# https://github.com/izimobil/polib/pulls/95

    Beyond solving the error comparing entries in polib, declares the
    argument ``compare_obsolete`` used to compare entries without consider
    if are obsoletes or not.
    """
    if compare_obsolete:
        if self.obsolete != other.obsolete:
            if self.obsolete:
                return -1
            else:
                return 1
    occ1 = sorted(self.occurrences[:])
    occ2 = sorted(other.occurrences[:])
    if occ1 > occ2:
        return 1
    if occ1 < occ2:
        return -1
    msgctxt = self.msgctxt or '0'
    othermsgctxt = other.msgctxt or '0'
    if msgctxt > othermsgctxt:
        return 1
    elif msgctxt < othermsgctxt:
        return -1
    msgid_plural = self.msgid_plural or '0'
    othermsgid_plural = other.msgid_plural or '0'
    if msgid_plural > othermsgid_plural:
        return 1
    elif msgid_plural < othermsgid_plural:
        return -1
    msgstr_plural = self.msgstr_plural or '0'
    othermsgstr_plural = other.msgstr_plural or '0'
    if msgstr_plural > othermsgstr_plural:
        return 1
    elif msgstr_plural < othermsgstr_plural:
        return -1
    if self.msgid > other.msgid:
        return 1
    elif self.msgid < other.msgid:
        return -1
    if self.msgstr > other.msgstr:
        return 1
    elif self.msgstr < other.msgstr:
        return -1
    return 0


POEntry.__cmp__ = _poentry__cmp__
