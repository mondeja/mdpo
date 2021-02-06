"""HTML utilities for mdpo."""


def html_attrs_tuple_to_string(attrs):
    """Converts a set of HTML attributes tuple to an HTML string.

    Converts all HTML attributes returned by
    :py:meth:`html.parser.HTMLParser.handle_starttag` ``attrs`` value into
    their original HTML representation.

    Args:
        attrs (list): List of attributes, each item being a tuple with two
            values, the attribute name as the first and the value as the
            second.

    Returns:
        str: HTML attributes string ready to be used inside a HTML tag.
    """
    response = ''
    for i, (name, value) in enumerate(attrs):
        response += '%s' % name
        if value is not None:
            response += '="%s"' % value
        if i < len(attrs) - 1:
            response += ' '
    return response


def get_html_attrs_tuple_attr(attrs, attrname):
    """Returns the value of an attribute from an attributes tuple.

    Given a list of tuples returned by an ``attrs`` argument value from
    :py:meth:`html.parser.HTMLParser.handle_starttag` method, and an attribute
    name, returns the value of that attribute.

    Args:
        attrs (list): List of tuples returned by
            :py:meth:`html.parser.HTMLParser.handle_starttag` method ``attrs``
            argument value.
        attrname (str): Name of the attribute whose value will be returned.

    Returns:
        str: Value of the attribute, if found, otherwise ``None``.
    """
    response = None
    for name, value in attrs:
        if name == attrname:
            response = value
            break
    return response
