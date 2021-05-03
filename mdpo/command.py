"""mdpo HTML commands related utilities."""

import re

from mdpo.text import removeprefix


COMMAND_SEARCH_RE = re.compile(r'<\!\-\-\s{0,}([^\s]+)\s{0,}([\w\s]+)?\-\->')

MDPO_COMMANDS = [
    'context',
    'disable',
    'disable-next-line',
    'enable',
    'enable-next-line',
    'include',
    'include-codeblock',
    'include-codeblocks',
    'disable-codeblock',
    'disable-codeblocks',
    'translator',
]


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
    command_match = COMMAND_SEARCH_RE.search(value)
    return command_match.groups() if command_match else (None, None)


def normalize_mdpo_command(value):
    """Normalizes a valid command and returns None if the command is invalid.

    This function works for lazy command validation (the user doesn't need
    to specify the ``mdpo-`` prefix used for command names).

    Args:
        value (str): Command to be normalized.

    Returns:
        str or None: Normalized command or None if is invalid.
    """
    if not value.startswith('mdpo-'):
        value = f'mdpo-{value}'
    return value if removeprefix(value, 'mdpo-') in MDPO_COMMANDS else None


def normalize_mdpo_command_aliases(command_aliases):
    """Validates and normalizes a mapping of mdpo command aliases.

    Args:
        command_aliases (dict): Aliases for mdpo commands, in the form
            ``{"<new-command-name>": "<mdpo-command>"}``.

    Raises:
        ValueError: if an mdpo command resolution doesn't exists.

    Returns:
        dict: Mapping validated and normalized.
    """
    response = {}
    for alias, mdpo_command in command_aliases.items():
        valid_mdpo_command = normalize_mdpo_command(mdpo_command)
        if not valid_mdpo_command:
            valid_mdpo_command_names_string = ', '.join(
                (f"'{cmd}'" for cmd in get_valid_mdpo_command_names()),
            )
            raise ValueError(
                f"Invalid mdpo command resolution '{mdpo_command}'."
                f' Valid values are: {valid_mdpo_command_names_string}',
            )
        response[alias] = valid_mdpo_command
    return response


def get_valid_mdpo_command_names():
    """Return valid mdpo commands names, with and without "mdpo-" prefix.

    Returns:
        list: Valid mdpo command names.
    """
    response = []
    for mdpo_command in MDPO_COMMANDS:
        response.append(f'mdpo-{mdpo_command}')
        response.append(mdpo_command)
    return response
