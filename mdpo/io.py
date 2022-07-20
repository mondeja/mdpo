"""mdpo I/O utilities."""

import glob
import os
from contextlib import contextmanager


@contextmanager
def environ(**env):
    """Overwrite temporarily some environment variables."""
    original_env = {key: os.getenv(key) for key in env}
    os.environ.update(env)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value


def filter_paths(filepaths, ignore_paths=[]):
    """Filter a list of paths removing those defined in other list of paths.

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


def to_files_or_content(value):
    """File path/glob/content disambiguator.

    Check if the value passed is a glob, a set of files in a list or is string
    content.

    Args:
        value (str): Value to check.

    Returns:
        tuple: Two values being the first a boolean that indicates if ``value``
        is a list of files (``True``) or string content (``False``) and the
        second value is the content, which could be an iterator (if a glob or
        a list of files is passed or a string).
    """
    try:
        parsed = glob.glob(value)
    except TypeError:
        # inferes list
        return (True, value)
    except Exception as err:
        # some strings like '[s-m]' will produce
        # 're.error: bad character range ... at position'
        if err.__module__ == 're' and err.__class__.__name__ == 'error':
            return (False, value)
        raise err
    if not parsed:
        # assumes it is content
        return (False, value)
    return (True, parsed)


def save_file_checking_file_changed(filepath, content, encoding='utf-8'):
    """Save a file checking if the content has changed.

    Args:
        pofile (:py:class:`polib.POFile`): PO file to save.
        po_filepath (str): Path to the new file to save in.

    Returns:
        bool: If the PO file content has been changed.
    """
    if not os.path.isfile(filepath):
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        return True

    with open(filepath, encoding=encoding) as f:
        prev_content = f.read()
    changed = prev_content != content
    if changed:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
    return changed
