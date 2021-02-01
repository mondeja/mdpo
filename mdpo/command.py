"""mdpo commands related utilities."""

import re


COMMAND_SEARCH_RE = re.compile(
    r'<\!\-\-\s{0,1}mdpo\-([a-z\-]+)\s{0,1}([\w\s]+)?\-\->',
)


def search_html_command(text):
    """Search a mdpo HTML command inside text."""
    command_search = COMMAND_SEARCH_RE.search(text)
    if command_search:
        return command_search.groups()
    return (None, None)
