"""mdpo commands related utilities."""

import re


COMMAND_SEARCH_RE = re.compile(
    r'<\!\-\-\s{0,1}mdpo\-([a-z\-]+)\s{0,1}([\w\s]+)?\-\->',
)


def parse_mdpo_html_command(value):
    """Parses a mdpo HTML command inside a string value.

    This function is used by md2po implementation to discover the HTML commands
    used by mdpo to customize the extraction.

    Args:
        value (str): Text where will a command will be searched.

    Returns:
        tuple: Namename of the command (not including the ``"mdpo"`` prefix)
        and its value.
    """
    command_search = COMMAND_SEARCH_RE.search(value)
    if command_search:
        return command_search.groups()
    return (None, None)
