"""Text utilities for mdpo."""


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
    """Returns the minimum possible of characters not found in a row for a string.
    For example, given the string ``"c cc cccc"`` and the character ``"c"``,
    returns the number of characters in a row that are not found, so ``3`` in
    this case.
    This function is used in the source code to compute the string that
    wraps markdown code spans. Given the code span
    ``"code that contains 3 ``` and 2 `` backticks"`` and the character
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


def striplastline(text):
    return '\n'.join(text.split('\n')[:-1])
