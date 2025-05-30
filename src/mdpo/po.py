"""PO files related stuff."""

import glob

import polib

from mdpo.io import filter_paths
from mdpo.polib import poentry__cmp__


def po_escaped_string(chars):
    r"""Prepend a ``\`` character to a string.

    This is used to escape values inside strings wrapped for the returned
    character.

    Args:
        chars (str): Value for which first character will be escaped.

    Returns:
        str: First character of passed string with ``\`` character prepended.
    """
    return f'\\{chars[0]}'


def find_entry_in_entries(entry, entries, **kwargs):
    """Return an equal entry in a set of :py:class:`polib.POEntry` entries.

    Finds the first :py:class:`polib.POEntry` instance in the iterable
    ``entries`` that is equal, according to its ``__cmp__`` method, to
    the :py:class:`polib.POEntry` instance passed as ``entry`` argument.

    Args:
        entry (:py:class:`polib.POEntry`): Entry to search for.
        entries (list): Entries to search against.
        **kwargs: Keyword arguments passed to :py:class:`polib.POEntry`
            ``__cmp__`` method.

    Returns:
        :py:class:`polib.POEntry`: Entry passed in ``entry`` argument if an
        equal entry has been found in ``entries`` iterable, otherwise ``None``.
    """
    response = None
    for compared_entry in entries:
        if poentry__cmp__(entry, compared_entry, **kwargs) == 0:
            response = compared_entry
            break
    return response


def mark_not_found_entries_as_obsoletes(
    pofile,
    entries,
):
    """Mark entries in a PO file obsoletes if are not in a set of entries.

    If an entry of the PO file is found in the set of entries, will be marked
    as no obsolete.

    Args:
        pofile (:py:class:`polib.POFile`): PO file in which the missing entries
            will be marked as obsoletes.
        entries (list): Entries to search against.
    """
    obsolete = False
    for entry in pofile:
        if not find_entry_in_entries(
            entry,
            entries,
            compare_occurrences=False,
        ):
            _equal_not_obsolete_found = find_entry_in_entries(
                entry,
                entries,
                compare_obsolete=False,
                compare_occurrences=False,
            )
            if _equal_not_obsolete_found:
                pofile.remove(entry)
            else:
                entry.obsolete = True
                obsolete = True
        else:
            entry.obsolete = False
    return obsolete


def remove_not_found_entries(pofile, entries):
    """Remove entries in a PO file if are not in a set of entries.

    Args:
        pofile (:py:class:`polib.POFile`): PO file for which the missing
            entries will be removed.
        entries (list): Entries to search against.
    """
    entries_to_remove = []
    for entry in pofile:
        if not find_entry_in_entries(
            entry,
            entries,
            compare_occurrences=False,
        ):
            _equal_not_obsolete_found = find_entry_in_entries(
                entry,
                entries,
                compare_obsolete=False,
                compare_occurrences=False,
            )
            if not _equal_not_obsolete_found:
                entries_to_remove.append(entry)
    for entry in entries_to_remove:
        pofile.remove(entry)


def pofiles_to_unique_translations_dicts(pofiles):
    """Extract unique translations from a set of PO files.

    Given multiple pofiles, extracts translations (those messages with non
    empty msgstrs) into two dictionaries, a dictionary for translations
    with contexts and other without them.

    Args:
        pofiles (list): List of :py:class:`polib.POFile` objects.

    Returns:
        tuple: dictionaries with translations.
    """
    translations, translations_with_msgctxt = {}, {}
    for pofile in pofiles:
        for entry in pofile:
            if entry.msgctxt:
                if entry.msgctxt not in translations_with_msgctxt:
                    translations_with_msgctxt[entry.msgctxt] = {}
                translations_with_msgctxt[
                    entry.msgctxt
                ][entry.msgid] = entry.msgstr
            else:
                translations[entry.msgid] = entry.msgstr
    return (translations, translations_with_msgctxt)


def paths_or_globs_to_unique_pofiles(pofiles_globs, ignore, po_encoding=None):
    """Convert any path, paths or glob to :py:class:`polib.POFile` objects.

    Args:
        pofiles_globs (str, list): Can be a path, a glob, multiples paths
            or multiples globs.
        ignore (list): Paths to ignore.
        po_encoding (str): Encoding used reading the PO files.

    Returns:
        set: Unique set of :py:class:`polib.POFile` objects.
    """
    if isinstance(pofiles_globs, str):
        pofiles_globs = [pofiles_globs]

    _po_filepaths, pofiles = ([], [])

    for pofiles_glob in pofiles_globs:
        for po_filepath in filter_paths(
            glob.glob(pofiles_glob),
            ignore_paths=ignore,
        ):
            if po_filepath not in _po_filepaths:
                pofiles.append(
                    polib.pofile(po_filepath, encoding=po_encoding),
                )
                _po_filepaths.append(po_filepath)

    return pofiles


def check_obsolete_entries_in_filepaths(filenames):
    """Warns about all obsolete entries found in a set of PO files.

    Args:
        filenames (list): Set of file names to check.

    Returns:
        list(str): error messages produced.
    """
    for filename in filenames:
        with open(filename, 'rb') as f:
            content_lines = f.readlines()

        yield from parse_obsoletes_from_content_lines(
            content_lines,
            location_prefix=f'{filename}:',
        )


def check_fuzzy_entries_in_filepaths(filenames):
    """Warns about all fuzzy entries found in a set of PO files.

    Args:
        filenames (list): Set of file names to check.

    Returns:
        list(str): error messages produced.
    """
    for filename in filenames:
        with open(filename, 'rb') as f:
            content_lines = f.readlines()

        yield from parse_fuzzy_from_content_lines(
            content_lines,
            location_prefix=f'{filename}:',
        )


def check_empty_msgstrs_in_filepaths(filenames):
    """Warns about all empty msgstr found in a set of PO files.

    Args:
        filenames (list): Set of file names to check.

    Returns:
        list(str): error messages produced.
    """
    for filename in filenames:
        with open(filename, 'rb') as f:
            content_lines = f.readlines()

        yield from parse_empty_msgstr_from_content_lines(
            content_lines,
            location_prefix=f'{filename}:',
        )


def parse_obsoletes_from_content_lines(
    content_lines,
    location_prefix='line ',
):
    """Warns about all obsolete entries found in a set of PO files.

    Args:
        content_lines (list): Set of content lines to check.
        location_prefix (str): Prefix to use in the location message.

    Returns:
        list(str): error locations found.
    """
    inside_obsolete_message = False
    for i, line in enumerate(content_lines):
        if not inside_obsolete_message and line[0:3] == b'#~ ':
            inside_obsolete_message = True

            yield f'{location_prefix}{i + 1}'
        elif inside_obsolete_message and line[0:3] != b'#~ ':
            inside_obsolete_message = False


def parse_fuzzy_from_content_lines(
    content_lines,
    location_prefix='line ',
):
    """Warns about all fuzzy entries found in a set of PO files.

    Args:
        content_lines (list): Set of content lines to check.
        location_prefix (str): Prefix to use in the location message.

    Returns:
        list(str): error locations found.
    """
    for i, line in enumerate(content_lines):
        if line.startswith(b'#,') and b'fuzzy' in line:
            yield f'{location_prefix}{i + 1}'


def parse_empty_msgstr_from_content_lines(
    content_lines,
    location_prefix='line ',
):
    """Warns about all empty msgstr found in a set of PO files.

    Args:
        content_lines (list): Set of content lines to check.
        location_prefix (str): Prefix to use in the location message.

    Returns:
        list(str): error locations found.
    """
    n_lines = len(content_lines)
    for i, line in enumerate(content_lines):
        if (
            line.startswith(b'msgstr ""') or line.startswith(b'#~ msgstr ""')
        ) and not content_lines[i - 1].startswith(b'msgid ""'):
            next_i = i + 1
            if next_i == n_lines or not content_lines[next_i].strip():
                yield f'{location_prefix}{next_i}'
