"""HTML utilities for mdpo."""


def html_attrs_tuple_to_string(attrs):
    """Converts a set of HTML attributes tuple to an HTML string."""
    response = ''
    for i, (name, value) in enumerate(attrs):
        response += '%s' % name
        if value is not None:
            response += '="%s"' % value
        if i < len(attrs) - 1:
            response += ' '
    return response


def get_html_attrs_tuple_attr(attrs, attrname):
    """Returns the value of an attribute from an attributes tuple given an
    attribute name."""
    response = None
    for name, value in attrs:
        if name == attrname:
            response = value
            break
    return response
