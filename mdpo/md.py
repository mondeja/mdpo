"""Markdown related utilities for mdpo."""

import re


def escape_links_titles(text, link_start_string='[', link_end_string=']'):
    """Finds titles inside inline links or images and escapes `"` characters
    found inside, returning the replaced string.
    """
    link_end_string_escaped_regex = re.escape(link_end_string)
    regex = r'({}[^{}]+{}\([^\s]+\s)([^\)]+)'.format(
        re.escape(link_start_string),
        link_end_string_escaped_regex,
        link_end_string_escaped_regex,
    )

    for match in re.findall(regex, text):
        original_string = match[0] + match[1]
        target_string = match[0] + '"%s"' % (
            match[1][1:-1].replace('"', '\\"')
        )
        text = text.replace(original_string, target_string)
    return text


def inline_untexted_links(text, link_start_string='[', link_end_string=']'):
    """Given a string like ``"String with [self-referenced-link]"``, replaces
    self referenced links markup characters by new ones, in this case
    ``"String with <self-referenced-link>"``. Only replaces links that do not
    contains hrefs.
    Wikilinks are not replaced (strings started with ``[[`` and ended with
    ``]]`` string chunks).
    """
    link_end_string_escaped_regex = re.escape(link_end_string)
    regex = r'({})([^{}]+)({})(?!\[|\()(?!\])'.format(
        re.escape(link_start_string),
        link_end_string_escaped_regex,
        link_end_string_escaped_regex,
    )
    return re.sub(regex, r'<\g<2>>', text)


def n_chars_until_chars(text, chars=[' ', '\n']):
    """Returns the number of characters until one of the characters passed
    as ``chars`` argument is found.
    """
    n = 1
    for ch in text:
        if ch in chars:
            break
        n += 1
    return n


def fixwrap_codespans(
    lines, code_start_string='`', code_end_string='`',
    width=80,
):
    """Given a set of lines wrapped by `:py:class:textwrap.TextWrapper`,
    unwraps reasonably all markdown codespans that are found inside the lines.
    This funcion is designed to render codespans without wrap them in multiples
    lines, which is desirable in markdown rendering based on available linters.
    """
    def _chars_num_until_next_codespan_exit(text):
        __exiting, __inside, __entering = (False, False, False)
        __n_backticks_wrapper, __n_backticks_to_exit = (0, None)
        n = 1
        _prev_char = None
        for _ch in text:
            if not __inside:
                if not __entering and not __exiting and \
                        _ch == code_start_string:
                    if _prev_char != '\\':
                        __entering = True
                        __n_backticks_wrapper += 1
                elif __entering and _ch != code_start_string:
                    __inside = True
                    __entering = False
                    __n_backticks_to_exit = __n_backticks_wrapper
                elif __entering and _ch == code_start_string:
                    if _prev_char != '\\':
                        __n_backticks_wrapper += 1
            elif __inside:
                if not __exiting and not __entering and \
                        _ch == code_end_string:
                    if _prev_char != '\\':
                        __exiting = True
                        __n_backticks_to_exit -= 1
                elif __exiting and _ch != code_end_string:
                    if __n_backticks_to_exit == 0:
                        break
                    else:
                        __exiting = False
                        __n_backticks_to_exit = __n_backticks_wrapper
                elif __exiting and _ch == code_end_string:
                    if _prev_char != '\\':
                        __n_backticks_to_exit -= 1
            _prev_char = _ch
            n += 1

        return n

    response = []

    _curr_line = ''

    _entering_codespan, _exiting_codespan, _inside_codespan = (
        False, False, False,
    )
    _codespan_n_backticks_wrapper, _n_backticks_to_exit_codespan = (0, None)
    prev_char = None
    for li, line in enumerate(lines):
        for ci, ch in enumerate(line):
            if not _inside_codespan:
                if not _entering_codespan and not _exiting_codespan and \
                        ch == code_start_string:

                    # check '`' escapes
                    if prev_char != '\\':
                        _entering_codespan = True
                        _codespan_n_backticks_wrapper += 1

                    # 70% of the line must be filled to wrap before codespans
                    if len(_curr_line) > width * .7:
                        _entering_codespan_length = \
                            _chars_num_until_next_codespan_exit(
                                line[ci:] + ' '.join(lines[li+1:]),
                            )
                        if len(_curr_line) + _entering_codespan_length > width:
                            response.append(_curr_line.rstrip(' '))
                            _curr_line = ''
                elif _entering_codespan and ch != code_start_string:
                    _inside_codespan = True
                    _entering_codespan = False
                    _n_backticks_to_exit_codespan = \
                        _codespan_n_backticks_wrapper
                elif _entering_codespan and ch == code_start_string:
                    if prev_char != '\\':
                        _codespan_n_backticks_wrapper += 1
            elif _inside_codespan:
                if not _exiting_codespan and not _entering_codespan and \
                        ch == code_end_string:
                    if prev_char != '\\':
                        _exiting_codespan = True
                        _n_backticks_to_exit_codespan -= 1
                elif _exiting_codespan and ch != code_end_string:
                    if _n_backticks_to_exit_codespan == 0:
                        _exiting_codespan = False
                        _inside_codespan = False
                        _codespan_n_backticks_wrapper = 0
                    else:
                        _exiting_codespan = False
                        _n_backticks_to_exit_codespan = \
                            _codespan_n_backticks_wrapper
                elif _exiting_codespan and ch == code_end_string:
                    if prev_char != '\\':
                        _n_backticks_to_exit_codespan -= 1

            if not _inside_codespan:
                if ch in [' ', '\n']:
                    # check if we can add more words until next space
                    _chars_until_next_space = n_chars_until_chars(
                        line[ci+1:] + ' ' + ' '.join(lines[li+1:]),
                    )
                    if len(_curr_line) + _chars_until_next_space > width:
                        response.append(_curr_line.rstrip(' '))
                        _curr_line = ''

            # store a reference to previous character
            prev_char = ch

            if ch == ' ' and not _curr_line:
                continue
            _curr_line += ch

        if not _inside_codespan:
            _chars_until_next_space = n_chars_until_chars(
                ' '.join(lines[li+1:]),
            )
            if len(_curr_line) + _chars_until_next_space > width:
                response.append(_curr_line.rstrip(' '))
                _curr_line = ''
            elif _curr_line:
                _curr_line += ' '
        elif _curr_line:
            _curr_line += ' '

    if _curr_line:
        response.append(_curr_line.rstrip(' '))
    return response
