"""Text utilities for mdpo."""

import os
import sys


def and_join(values):
    """Comma and space join using "and" between the last and penultimate items.

    Args:
        values (list): Values to join.
    """
    return ', '.join(values[:-1]) + f' and {values[-1]}'


def min_not_max_chars_in_a_row(char, text, default=1):
    r"""Return the minimum possible of characters not found in a row for a string.

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
        for n in range(1, max(in_a_rows) + 2):
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
    import re
    splits = re.split(
        re.compile(fr'([^\\]{separator})'),
        value.lstrip(r'\\'),
        maxsplit=1,
    )
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


def parse_strint_0_inf(value):
    """Parse a string to a integer accepting infinte values.

    Converts an integer passed as string in an integer or ``math.inf`` if
    the passed value is ``"0"`` or ``math.inf``.

    Args:
        value (str): Value to parse.
    """
    if isinstance(value, str) and value.lower() == 'nan':
        raise ValueError(f"invalid strict converting of '{value}' to number")

    num = float(value)
    try:
        return int(num) if num > 0 else float('inf')
    except OverflowError:  # cannot convert float infinity to integer
        return float('inf')


def parse_wrapwidth_argument(value):
    """Parse the argument ``-w/--wrapwidth``.

    Args:
        value (str): Wrapwidth value.
    """
    try:
        value = parse_strint_0_inf(value)
    except ValueError:
        if os.environ.get('_MDPO_RUNNING'):  # executed as CLI
            sys.stderr.write(
                f"Invalid value '{value}' for -w/--wrapwidth argument.\n",
            )
            sys.exit(1)
        raise ValueError(
            f"Invalid value '{value}' for wrapwidth argument.",
        )
    return value
