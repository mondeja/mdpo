"""Markdown related utilities for mdpo."""

import re

import md4c

from mdpo.text import min_not_max_chars_in_a_row


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


class MarkdownWrapper:
    __slots__ = {
        # arguments
        'width',
        'first_line_width',
        'md4c_extensions',

        'bold_start_string',
        'bold_end_string',
        'italic_start_string',
        'italic_end_string',
        'code_start_string',
        'code_end_string',
        'link_start_string',
        'link_end_string',
        'wikilink_start_string',
        'wikilink_end_string',

        # state
        'output',
        '_current_line',
        '_inside_aspan',
        '_inside_codespan',
        '_current_wikilink_target',
    }
    
    def __init__(
        self,
        width=80,
        first_line_width=80,
        md4c_extensions={},
        **kwargs,
    ):
        self.width = width
        self.first_line_width = first_line_width
        self.md4c_extensions = md4c_extensions
        
        self.output = ''
        self._current_line = ''
        
        self.bold_start_string = kwargs.get('bold_start_string', '**')
        self.bold_end_string = kwargs.get('bold_end_string', '**')
        self.italic_start_string = kwargs.get('italic_start_string', '*')
        self.italic_end_string = kwargs.get('italic_end_string', '*')
        self.code_start_string = kwargs.get('code_start_string', '`')[0]
        self.code_end_string = kwargs.get('code_end_string', '`')[0]
        self.link_start_string = kwargs.get('link_start_string', '[')
        self.link_end_string = kwargs.get('link_end_string', ']')
        self.wikilink_start_string = kwargs.get('wikilink_start_string', '[[')
        self.wikilink_end_string = kwargs.get('wikilink_end_string', ']]')

        self._inside_aspan = False
        self._inside_codespan = False
        self._current_wikilink_target = None
    
    def _get_currently_applied_width(self):
        if not self.output:
            return self.first_line_width
        return self.width
    
    def enter_block(self, block, details):
        pass
    
    def leave_block(self, block, details):
        pass
    
    def enter_span(self, span, details):        
        if span is md4c.SpanType.CODE:
            self._inside_codespan = True
            self._current_line += self.code_start_string
        elif span is md4c.SpanType.A:
            self._inside_aspan = True
            self._current_line += self.link_start_string
        elif span is md4c.SpanType.STRONG:
            self._current_line += self.bold_start_string
        elif span is md4c.SpanType.EM:
            self._current_line += self.italic_start_string
        elif span is md4c.SpanType.WIKILINK:
            self._current_line += self.wikilink_start_string
            self._current_wikilink_target = details['target'][0][1]

    def leave_span(self, span, details):
        if span is md4c.SpanType.CODE:
            self._inside_codespan = False
            self._current_line += self.code_end_string
        elif span is md4c.SpanType.A:
            self._inside_aspan = False
            href = details['href'][0][1]
            self._current_line += f'{self.link_end_string}({href}'
            
            self._current_line += ')'
        elif span is md4c.SpanType.STRONG:
            self._current_line += self.bold_end_string
        elif span is md4c.SpanType.EM:
            self._current_line += self.italic_end_string
        elif span is md4c.SpanType.WIKILINK:
            self._current_line += self.wikilink_end_string
            self._current_wikilink_target = None
    
    def text(self, block, text):
        # print(f"TEXT: '{text}'")
        
        if self._inside_codespan:
            width = self._get_currently_applied_width()

            if len(self._current_line) + len(text) + 1 > width:
                self._current_line = self._current_line.rstrip('`').rstrip(' ')
                self.output += f'{self._current_line}\n'
                self._current_line = '`'

            n_backticks = min_not_max_chars_in_a_row(
                self.code_start_string[0],
                text,
            ) - 1
            if n_backticks:
                self._current_line += n_backticks * '`'

            self._current_line += f'{text}{n_backticks * "`"}'
        else:
            if self._current_wikilink_target:
                if text != self._current_wikilink_target:
                    self._current_line += (
                        f'{self._current_wikilink_target}|{text}'
                    )
                else:
                    self._current_line += text
                return
            
            text_splits = text.split(' ')
            width = self._get_currently_applied_width()
            if self._inside_aspan:  # links wrapping
                if len(self._current_line) + len(text_splits[0]) + 1 > width:
                    # new link text in newline
                    self._current_line = self._current_line[:-1].rstrip(' ')
                    self.output += f'{self._current_line}\n'
                    self._current_line = '['
                width *= .95        # latest word in newline
            
            for i, text_split in enumerate(text_splits):
                # +1 is a space here
                if len(self._current_line) + len(text_split) + 1 > width:
                    if i or (self._current_line and self._current_line[-1] == ' '):
                        self.output += f'{self._current_line}\n'
                        self._current_line = ''
                        width = self._get_currently_applied_width()
                        if self._inside_aspan:
                            width *= .95
                    elif not self._inside_aspan and i and i + 1 <= len(text_splits):
                        self._current_line += ' '
                elif i:
                    self._current_line += ' '
                self._current_line += text_split
    
    def wrap(self, text):
        """Wraps reasonably Markdown lines."""
        parser = md4c.GenericParser(
            0,
            **{ext: True for ext in self.md4c_extensions},
        )
        parser.parse(
            text,
            self.enter_block,
            self.leave_block,
            self.enter_span,
            self.leave_span,
            self.text,
        )
        
        if self._current_line:
            self.output += f'{self._current_line}'
        if self.first_line_width == self.width:  # is not blockquote nor list
            self.output += '\n'
        return self.output


def fixwrap_codespans(
    lines,
    code_start_string='`',
    code_end_string='`',
    width=80,
    first_line_width=80,
):
    """

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

    # Response
    response = []
    _width = first_line_width

    # State
    _curr_line = ''

    _entering_codespan = False
    _exiting_codespan = False
    _inside_codespan = False

    _codespan_n_backticks_wrapper = 0
    _n_backticks_to_exit_codespan = None

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
