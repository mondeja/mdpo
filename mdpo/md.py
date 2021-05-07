"""Markdown related utilities for mdpo."""

import re


LINK_REFERENCE_RE = re.compile(
    r'^\s{0,3}\[([^\]]+)\]:\s+<?([^\s>]+)>?\s*["\'\(]?([^"\'\)]+)?',
)


def escape_links_titles(text, link_start_string='[', link_end_string=']'):
    r"""Escapes ``"`` characters found inside link titles.

    This is used by mdpo extracting titles of links which contains Markdown
    `link titles <https://spec.commonmark.org/0.29/#link-title>`_ delimiter
    characters.

    Args:
        text (str): Text where the links titles to escape will be searched.
        link_start_string (str): String that delimites the start of a link.
        link_end_string (str): String that delimites the end of a link.

    Returns:
        str: Same text as input with escaped title delimiters characters found
        inside titles.

    Examples:
        >>> title = '[a link](href "title with characters to escape "")'
        >>> escape_links_titles(title)
        '[a link](href "title with characters to escape \\"")'
    """
    link_end_string_escaped_regex = re.escape(link_end_string)
    regex = re.compile(
        r'({}[^{}]+{}\([^\s]+\s)([^\)]+)'.format(
            re.escape(link_start_string),
            link_end_string_escaped_regex,
            link_end_string_escaped_regex,
        ),
    )

    for match in re.findall(regex, text):
        original_string = match[0] + match[1]
        target_string = match[0] + '"%s"' % (
            match[1][1:-1].replace('"', '\\"')
        )
        text = text.replace(original_string, target_string)
    return text


def inline_untexted_links(text, link_start_string='[', link_end_string=']'):
    """Replace Markdown self-referenced links delimiters by ``<`` and ``>``.

    Given a string like ``"Text with [self-referenced-link]"``, replaces self
    referenced links markup characters by new ones, in this case would becomes
    ``"Text with <self-referenced-link>"``.

    Wikilinks are not replaced (strings started with ``[[`` and ended with
    ``]]`` string chunks).

    Args:
        text (str): Text that could contain self-referenced links.
        link_start_string (str): String that delimites the start of a link.
        link_end_string (str): String that delimites the end of a link.

    Returns:
        str: Same text as input with replaced link delimiters characters found
        inside titles.

    Examples:
        >>> inline_untexted_links('Text with [self-referenced-link]')
        'Text with <self-referenced-link>'
    """
    return re.sub(
        (
            re.escape(link_start_string) + r'(\w{1,5}:\/\/[^\s]+)' +
            re.escape(link_end_string)
        ), r'<\g<1>>', text,
    )


def n_chars_until_chars(text, chars=[' ', '\n']):
    """Computes number of characters until one of other characters are found.

    In a string, returns the minimum position of one of the characters passed
    as ``chars`` argument, using an one-based index. If any of the characters
    are found, returns the length of the string.

    Args:
        text (str): Text to search for the characters.
        chars (str): Characters to search.

    Returns:
        int: Number of characters, starting at one, of the first character
        found in the text passed.

    Examples:
        >>> n_chars_until_chars('abc', chars=['b', 'c'])
        2

        >>> n_chars_until_chars('foo', chars=['b', 'a', 'r'])
        3
    """
    response = len(text)
    for char in chars:
        try:
            value = text.index(char) + 1
        except ValueError:
            pass
        else:
            if value < response:
                response = value
    return response


def parse_link_references(content):
    """Parses link references found in a Markdown content.

    Args:
        content (str): Markdown content to be parsed.

    Returns:
        list: Tuples with 3 values, target, href and title for each link
            reference.
    """
    response = []
    for line in content.splitlines():
        linestrip = line.strip()
        if linestrip and linestrip[0] == '[':
            match = re.search(LINK_REFERENCE_RE, linestrip)
            if match:
                response.append(match.groups())
    return response


def fixwrap_codespans(
    lines,
    code_start_string='`',
    code_end_string='`',
    width=80,
    first_line_width=80,
):
    """Wraps reasonably Markdown lines containing codespans.

    Given a set of lines wrapped by `:py:class:textwrap.TextWrapper`,
    unwraps reasonably all markdown codespans that are found inside the lines.
    This funcion is designed to render codespans without wrap them in multiples
    lines, which is desirable in markdown rendering.

    Args:
        lines (list): Markdown lines as are returned by
            :py:func:`textwrap.wrap`.
        code_start_string (str): String that delimites the start of a codespan.
        code_end_string (str): String that delimites the end of a codespan.
        width (int): Result line width.
        first_line_width (int): First line width in result.

    Returns:
        list: Lines with codespans propertly wrapped.
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
    _width = first_line_width

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
                    _curr_line_len = len(_curr_line)
                    if _curr_line_len > _width * .7:
                        _entering_codespan_length = \
                            _chars_num_until_next_codespan_exit(
                                line[ci:] + ' '.join(lines[li+1:]),
                            )
                        if _curr_line_len + _entering_codespan_length > _width:
                            response.append(_curr_line.rstrip(' '))
                            _curr_line = ''
                            _width = width  # not in first line now
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
                    if len(_curr_line) + _chars_until_next_space > _width:
                        response.append(_curr_line.rstrip(' '))
                        _curr_line = ''
                        _width = width  # not in first line now

            # store a reference to previous character
            prev_char = ch

            if ch == ' ' and not _curr_line:
                continue
            _curr_line += ch

        if not _inside_codespan:
            _chars_until_next_space = n_chars_until_chars(
                ' '.join(lines[li+1:]),
            )
            if len(_curr_line) + _chars_until_next_space > _width:
                response.append(_curr_line.rstrip(' '))
                _curr_line = ''
                _width = width  # not in first line now
            elif _curr_line:
                _curr_line += ' '

    if _curr_line:
        response.append(_curr_line.rstrip(' '))
        _width = width  # not in first line now
    return response
