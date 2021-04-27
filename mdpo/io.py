"""mdpo I/O utilities."""

import glob
import os
import re


def filter_paths(filepaths, ignore_paths=[]):
    """Filters a list of paths removing those defined in other list of paths.

    The paths to filter can be defined in the list of paths to ignore in
    several forms:

    - The same string.
    - Only the file name.
    - Only their direct directory name.
    - Their direct directory full path.

    Args:
        filepaths (list): Set of source paths to filter.
        ignore_paths (list): Paths that must not be included in the response.

    Returns:
        list: Non filtered paths ordered alphabetically.
    """
    response = []
    for filepath in filepaths:
        # ignore by filename
        if os.path.basename(filepath) in ignore_paths:
            continue
        # ignore by dirname
        if os.path.basename(os.path.dirname(filepath)) in ignore_paths:
            continue
        # ignore by filepath
        if filepath in ignore_paths:
            continue
        # ignore by dirpath (relative or absolute)
        if (os.sep).join(filepath.split(os.sep)[:-1]) in ignore_paths:
            continue
        response.append(filepath)
    response.sort()
    return response


def to_file_content_if_is_file(value, encoding='utf-8'):
    """Check if the value passed is a file path or string content.

    If is a file, reads its content and returns it, otherwise returns
    the string passed as is.

    Args:
        value (str): Value to check if is a filepath or content.
        encoding (str): Expected file encoding, if is a file.

    Returns:
        str: File content if ``value`` is an existing file or ``value`` as is.
    """
    if os.path.isfile(value):
        with open(value, encoding=encoding) as f:
            value = f.read()
    return value


def to_glob_or_content(value):
    """Check if the value passed is a glob or is string content.

    Args:
        value (str): Value to check if is a glob or content.

    Returns:
        list: Two values being the first a boolean that indicates if ``value``
        is a glob (``True``) or content (``False``) and the second value
        is the content (parsed as glob is first value is ``True``).
    """
    try:
        parsed = glob.glob(value)
    except re.error:
        # some strings like '[s-m]' will produce
        # 're.error: bad character range ... at position'
        return (False, value)
    if not parsed:
        # assumes it is content
        return (False, value)
    return (True, parsed)
