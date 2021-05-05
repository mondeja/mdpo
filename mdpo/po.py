"""``.po`` files related stuff."""


def po_escaped_string(chars):
    r"""Convenience function that prepends a ``\`` character to a string.

    This is used to escape values inside strings wrapped for the returned
    character.

    Args:
        chars (str): Value for which first character will be escaped.

    Returns:
        str: First character of passed string with ``\`` character prepended.
    """
    return '\\' + chars[0]


def find_entry_in_entries(entry, entries, **kwargs):
    """Returns an equal entry in a set of :py:class:`polib.POEntry` entries.

    Finds the first :py:class:`polib.POEntry` instance in the iterable
    ``entries`` that is equal, according to its ``__cmp__`` method, to
    the :py:class:`polib.POEntry` instance passed as ``entry`` argument.

    Args:
        entry (:py:class:`polib.POEntry`): Entry to search for.
        entries (list): Entries to search against.
        **kwargs: Keyword arguments passed to :py:meth:`polib.POEntry.__cmp__`.

    Returns:
        :py:class:`polib.POEntry`: Entry passed in ``entry`` argument if an
        equal entry has been found in ``entries`` iterable, otherwise ``None``.
    """
    response = None
    for compared_entry in entries:
        if entry.__cmp__(compared_entry, **kwargs) == 0:
            response = compared_entry
            break
    return response


def mark_not_found_entries_as_obsoletes(
    pofile,
    entries,
):
    """Marks entries in a PO file obsoletes if are not in a set of entries.

    If an entry of the PO file is found in the set of entries, will be marked
    as no obsolete.

    Args:
        pofile (:py:class:`polib.POFile`): PO file in which the missing entries
            will be marked as obsoletes.
        entries (list): Entries to search against.
    """
    for entry in pofile:
        if entry not in entries:
            _equal_not_obsolete_found = find_entry_in_entries(
                entry,
                entries,
                compare_obsolete=False,
            )
            if _equal_not_obsolete_found:
                pofile.remove(entry)
            else:
                entry.obsolete = True
        else:
            entry.obsolete = False


def remove_not_found_entries(pofile, entries):
    """Removes entries in a PO file if are not in a set of entries.

    Args:
        pofile (:py:class:`polib.POFile`): PO file for which the missing
            entries will be removed.
        entries (list): Entries to search against.
    """
    for entry in pofile:
        if entry not in entries:
            _equal_not_obsolete_found = find_entry_in_entries(
                entry,
                entries,
                compare_obsolete=False,
            )
            if not _equal_not_obsolete_found:
                pofile.remove(entry)
