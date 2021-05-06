"""Text utilities for mdpo."""

import re
import textwrap


def max_char_in_a_row(char, text):
    """Returns the maximum numbers of characters in a row found inside a string.

    Args:
        char (str): Character to search.
        text (str): Text inside which find the character repeated in a row.

    Returns:
        int: Maximum repeats in a row of the character inside the text.
    """
    response, partial_response = (0, 0)
    _in_the_row = False

    for ch in text:
        if ch == char:
            partial_response += 1
            _in_the_row = True
        elif _in_the_row:
            _in_the_row = False
            response = max(response, partial_response)
            partial_response = 0
    return max(response, partial_response)


def min_not_max_chars_in_a_row(char, text, default=1):
    r"""Returns the minimum possible of characters not found in a row for a string.

    For example, given the string ``"c cc cccc"`` and the character ``"c"``,
    returns the minimum number of characters in a row that are not found, so
    ``3`` in this case.

    This function is used in the source code to compute the string that
    wraps markdown code spans. Given the code span
    ``"code that contains 3 \`\`\` and 2 \`\` backticks"`` and the character
    ``"`"``, this function returns  ``1``.

    Args:
        char (str): Character to search.
        text (str): Text inside which find the character repeated in a row.

    Returns:
        int: Minimum number possible of characters not found in a row.
    """
    in_a_rows, _current_in_a_row, _in_the_row = ([], 0, False)
    for ch in text:
        if ch == char:
            _current_in_a_row += 1
            _in_the_row = True
        elif _in_the_row:
            _in_the_row = False
            if _current_in_a_row not in in_a_rows:
                in_a_rows.append(_current_in_a_row)
            _current_in_a_row = 0
    if _in_the_row and _current_in_a_row not in in_a_rows:
        in_a_rows.append(_current_in_a_row)

    if in_a_rows:
        response = None
        for n in range(1, max(in_a_rows)+2):
            if n not in in_a_rows:
                response = n
                break
    else:
        response = default
    return response


def parse_escaped_pair(value, separator=':'):
    r"""Escapes a pair key-value separated by a character.

    The separator can be escaped using the character '\'.

    Args:
        value (str): String to be converted to a pair key-value.
        separator (str): Separator to use for the split.

    Raises:
        ValueError: The value doesn't contains an unescaped valid separator.

    Returns:
        tuple: Parsed key-value pair.
    """
    regex = re.compile(fr'([^\\]{separator})')

    splits = re.split(regex, value.lstrip(r'\\'), maxsplit=1)
    if len(splits) == 1:
        raise ValueError()
    return (
        (splits[0] + splits[1][0]).replace(rf'\\{separator}', separator, 1),
        splits[2].lstrip(),
    )


def parse_escaped_pairs(pairs, separator=':'):
    r"""Escapes multiples pairs key-value separated by a character.

    The separator can be escaped using the character '\'.

    Args:
        pairs (list): List of texts to parse.
        separator (str): Separator to use for the splits.

    Raises:
        ValueError: A value doesn't contains an unescaped valid separator.
        KeyError: Repeated keys in pairs.

    Returns:
        dict: Key-value pairs.
    """
    response = {}
    for pair in pairs:
        try:
            key, value = parse_escaped_pair(pair, separator=separator)
        except ValueError:
            raise ValueError(pair)
        if key in response:
            raise KeyError(key)
        response[key] = value
    return response


def wrap_different_first_line_width(
    text,
    width=80,
    first_line_width_diff=0,
    **kwargs,
):
    """Wraps lines using a different width for first line.

    Uses :py:func:`wrap.textwrap`, but the first line is wrapped with a
    different width.

    Args:
        text (str): Text to wrap in lines.
        width (int): Lines maximum width.
        first_line_width_diff (int): Difference in width against the ``width``
            parameter used for the first line.
        **kwargs: Additional optional arguments passed to
            :py:func:`wrap.textwrap` function.

    Returns:
        list: Wrapped lines.
    """
    if len(text) > width - first_line_width_diff:
        # correct wrapping for list items
        li_first_line = textwrap.wrap(
            text,
            width=width + first_line_width_diff,
            max_lines=4,
            placeholder='?',
            **kwargs,
        )[0]
        li_subsequent_lines = textwrap.wrap(
            text[len(li_first_line):],
            width=width,
            **kwargs,
        )
        li_subsequent_lines[0] = li_subsequent_lines[0].lstrip()
        return [
            li_first_line,
            *li_subsequent_lines,
        ]

    return textwrap.wrap(
        text,
        width=width,
        **kwargs,
    )


def striplastline(text):
    """Returns a text, ignoring the last line.

    Args:
        text (str): Text that will be returned ignoring its last line.

    Returns:
        str: Text wihout their last line.
    """
    return '\n'.join(text.split('\n')[:-1])


def removeprefix(text, prefix):
    """Removes a prefix from a string.

    If the string starts with the prefix string, return string[len(prefix):].
    Otherwise, returns the original string. This function has been added in
    Python3.9 as the builtin `str.removeprefix`, but is defined here to support
    previous versions of the language.

    Args:
        text (str): Value whose prefix will be removed.
        prefix (str): Prefix to remove.

    Returns:
        str: Text without the prefix, if that prefix exists in the text.
    """
    if hasattr(str, 'removeprefix'):
        return text.removeprefix(prefix)
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def removesuffix(text, suffix):
    """Removes a suffix from a string.

    If the string ends with the suffix string and the suffix is not empty,
    returns string[:-len(suffix)]. Otherwise, returns the original string.
    This function has been added in Python3.9 as the builtin
    `str.removesuffix`, but is defined here to support previous versions of
    the language.

    Args:
        text (str): Value whose suffix will be removed.
        suffix (str): Suffix to remove.

    Returns:
        str: Text without the suffix, if that suffix exists in the text.
    """
    if hasattr(str, 'removesuffix'):
        return text.removesuffix(suffix)
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text
