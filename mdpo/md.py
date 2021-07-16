"""Markdown related utilities for mdpo."""

import re

import md4c

from mdpo.po import po_escaped_string
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


class MarkdownSpanWrapper:
    __slots__ = {
        # arguments
        'width',
        'first_line_width',
        'indent',
        'first_line_indent',
        'md4c_extensions',

        'bold_start_string',
        'bold_end_string',
        'italic_start_string',
        'italic_start_string_escaped',
        'italic_end_string',
        'italic_end_string_escaped',
        'code_start_string',
        'code_start_string_escaped',
        'code_end_string',
        'code_end_string_escaped',
        'link_start_string',
        'link_end_string',
        'wikilink_start_string',
        'wikilink_end_string',

        # state
        'output',
        '_current_line',
        '_current_aspan_href',
        '_current_aspan_title',
        '_inside_codespan',
        '_current_wikilink_target',
    }

    def __init__(
        self,
        width=80,
        first_line_width=80,
        indent='',
        first_line_indent='',
        md4c_extensions={},
        **kwargs,
    ):
        self.width = width
        self.first_line_width = first_line_width
        self.indent = indent
        self.first_line_indent = first_line_indent
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

        self.italic_start_string_escaped = kwargs.get(
            'italic_start_string_escaped',
            po_escaped_string(self.italic_start_string),
        )
        self.italic_end_string_escaped = kwargs.get(
            'italic_end_string_escaped',
            po_escaped_string(self.italic_end_string),
        )
        self.code_start_string_escaped = kwargs.get(
            'code_start_string_escaped',
            po_escaped_string(self.code_start_string),
        )
        self.code_end_string_escaped = kwargs.get(
            'code_end_string_escaped',
            po_escaped_string(self.code_end_string),
        )

        self._current_aspan_href = None
        self._current_aspan_title = None
        self._inside_codespan = False
        self._current_wikilink_target = None

    def _get_currently_applied_width(self):
        return self.width if self.output else self.first_line_width

    def _get_currently_applied_indent(self):
        return self.indent if self.output else self.first_line_indent

    def enter_block(self, block, details):
        pass

    def leave_block(self, block, details):
        pass

    def enter_span(self, span, details):
        if span is md4c.SpanType.CODE:
            self._inside_codespan = True
            self._current_line += self.code_start_string
        elif span is md4c.SpanType.A:
            self._current_line += self.link_start_string
            self._current_aspan_href = details['href'][0][1]
            self._current_aspan_title = (
                details['title'][0][1] if details['title'] else None
            )
        elif span is md4c.SpanType.STRONG:
            self._current_line += self.bold_start_string
        elif span is md4c.SpanType.EM:
            self._current_line += self.italic_start_string
        elif span is md4c.SpanType.WIKILINK:
            self._current_line += self.wikilink_start_string
            self._current_wikilink_target = details['target'][0][1]
        elif span is md4c.SpanType.IMG:
            self._current_line += '!['

    def leave_span(self, span, details):
        if span is md4c.SpanType.CODE:
            self._inside_codespan = False
            self._current_line += self.code_end_string
        elif span is md4c.SpanType.A:
            if self._current_line[-1] != '>':
                self._current_line += f']({self._current_aspan_href}'
                if self._current_aspan_title:
                    self._current_line += (
                        f' "{escape_links_titles(self._current_aspan_title)}"'
                    )
                self._current_line += ')'
            self._current_aspan_href = False
            self._current_aspan_href = None
            self._current_aspan_title = None
        elif span is md4c.SpanType.STRONG:
            self._current_line += self.bold_end_string
        elif span is md4c.SpanType.EM:
            self._current_line += self.italic_end_string
        elif span is md4c.SpanType.WIKILINK:
            self._current_line += self.wikilink_end_string
            self._current_wikilink_target = None
        elif span is md4c.SpanType.IMG:
            src = details['src'][0][1]
            self._current_line += f']({src}'
            if details['title']:
                title = details['title'][0][1]
                self._current_line += f' "{escape_links_titles(title)}"'
            self._current_line += ')'

    def text(self, block, text):
        if self._inside_codespan:
            width = self._get_currently_applied_width()
            indent = self._get_currently_applied_indent()

            if len(self._current_line) + len(text) + 1 > width:
                self._current_line = self._current_line.rstrip('`').rstrip(' ')
                self.output += f'{indent}{self._current_line}\n'
                self._current_line = '`'

            n_backticks = min_not_max_chars_in_a_row(
                self.code_start_string[0],
                text,
            ) - 1
            if n_backticks:
                self._current_line += n_backticks * '`'

            self._current_line += f'{text}{n_backticks * "`"}'
        elif self._current_wikilink_target:
            if text != self._current_wikilink_target:
                self._current_line += (
                    f'{self._current_wikilink_target}|{text}'
                )
            else:
                self._current_line += text
            return
        else:
            if self._current_aspan_href:
                if (
                    self._current_aspan_href == text
                    and not self._current_aspan_title
                ):
                    self._current_line = (
                        f"{self._current_line.rstrip(' [')} <{text}>"
                    )
                    return

            if text == self.italic_start_string:
                text = self.italic_start_string_escaped
            elif text == self.code_start_string:
                text = self.code_start_string_escaped
            elif text == self.code_end_string:  # pragma: no cover
                text = self.code_end_string_escaped
            elif text == self.italic_end_string:  # pragma: no cover
                text = self.italic_end_string_escaped

            text_splits = text.split(' ')
            width = self._get_currently_applied_width()
            if self._current_aspan_href:  # links wrapping
                if len(self._current_line) + len(text_splits[0]) + 1 > width:
                    indent = self._get_currently_applied_indent()
                    # new link text in newline
                    self._current_line = self._current_line[:-1].rstrip(' ')
                    self.output += f'{indent}{self._current_line}\n'
                    self._current_line = '['
                width *= .95        # latest word in newline

            for i, text_split in enumerate(text_splits):
                # +1 is a space here
                if len(self._current_line) + len(text_split) + 1 > width:
                    if i or (
                        self._current_line and self._current_line[-1] == ' '
                    ):
                        indent = self._get_currently_applied_indent()
                        self.output += f'{indent}{self._current_line}\n'
                        self._current_line = ''
                        width = self._get_currently_applied_width()
                        if self._current_aspan_href:
                            width *= .95
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
            self.output += (
                f'{self._get_currently_applied_indent()}{self._current_line}'
            )
        if self.first_line_width == self.width:  # is not blockquote nor list
            self.output += '\n'
        return self.output
