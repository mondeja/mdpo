"""mdpo command line interface utilities."""


def parse_list_argument(text, splitter=','):
    return tuple(filter(None, text.split(splitter)))
