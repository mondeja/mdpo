"""Custom events executed during the parsing process of an implementation."""


def raise_skip_event(events, event_name, *event_args):
    """Execute all functions defined for an event of a parser.

    If a function returns ``False``, this function will return ``True`` meaning
    that an event is trying to skip the parsing for an element.

    Args:
        events (dict): Dictionary with all events defined.
        event_name (str): Name of the event whose functions will be executed.
        *event_args: Arguments propagated to the events functions.

    Returns:
        bool: ``True`` if an event function returns ``False``, ``False``
            otherwise.
    """
    try:
        pre_events = events[event_name]
    except KeyError:
        return False
    skip = False
    for event in pre_events:
        if event(*event_args) is False:
            skip = True
    return skip
