"""mdpo command line interface utilities."""


def parse_list_argument(value, splitter=','):
    """Converts values in a string separated by characters into a tuple.

    This function is needed by mdpo command line interfaces to convert
    some arguments values separated by commas into iterables.

    Args:
        value (str): String to be converted to list separating it by
            ``splitter`` argument value.
        splitter (str): Separator used for separate the ``value`` argument.

    Returns:
        tuple: Strings separated.
    """
    return tuple(filter(None, value.split(splitter)))
