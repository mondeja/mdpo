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
    """Returns an equal entry in a set of :py:class:polib.POEntry` entries.

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
