"""Workaround for polib issue and required improvement to make work mdpo.

See https://github.com/izimobil/polib/pulls for details.
"""


def poentry__cmp__(
    self,
    other,
    compare_obsolete=True,
    compare_msgstr=True,
    compare_occurrences=True,
):
    """Compare entries like ``__cmp__`` method of :py:class:`polib.POEntry`.

    This function add custom entries comparison capabilities to
    :py:class:`polib.POEntry`, needed by mdpo to prevent some errors.

    Args:
        self (:py:class:`polib.POEntry`): Entry to be compared.
        other (:py:class:`polib.POEntry`): Entry to compare against.
        compare_obsolete (bool): Indicates if the ``obsolete`` property of the
            entries will be used comparing them.
        compare_msgstr (bool): Indicates if the ``msgstr`` property of the
            entries will be used comparing them.
        compare_occurrences (bool): Indicates if the ``occurrences`` property
            of the entries will be used comparing them.
    """
    if compare_obsolete:
        if self.obsolete != other.obsolete:
            if self.obsolete:
                return -1
            else:
                return 1
    if compare_occurrences:
        # `.copy` is an equivalent for full slice [:], but is faster
        # `.copy` doesn't exists for lists in Python2 so for this reason,
        # this change has not been introduced in polib
        occ1 = sorted(self.occurrences.copy())
        occ2 = sorted(other.occurrences.copy())
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
    elif self.msgid > other.msgid:
        return 1
    elif self.msgid < other.msgid:
        return -1
    if compare_msgstr:
        if self.msgstr > other.msgstr:
            return 1
        elif self.msgstr < other.msgstr:
            return -1
    return 0
