"""Custom events executed during the parsing process of an implementation."""

import sys


def raise_skip_event(events, event_name, *event_args):
    """Execute all functions defined for an event of a parser.

    If a function returns ``False``, this function will return ``True`` meaning
    that an event is trying to skip the associated function.

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


def _block_msg(block, details):
    if details:
        return f'{block.name} - {details}'
    return block.name


def debug_events(program):
    """Debugging events for interfaces. Displays in STDOUT all event targets.

    Args:
        program (str): Command line interface name, to display it at the
            beginning of the output.

    Returns:
        dict: Event target printing functions.
    """
    def debug(event, msg):
        import datetime

        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        sys.stdout.write(f'{program}[DEBUG]::{date}::{event}:: {msg}\n')

    def print_msgid(self, msgid, msgstr, msgctxt, tcomment, flags):
        msg = f'msgid=\'{msgid}\''
        if msgstr:
            msg += f' - msgstr=\'{msgstr}\''
        if msgctxt:
            msg += f' - msgctxt=\'{msgctxt}\''
        if tcomment:
            msg += f' - tcomment=\'{tcomment}\''
        if flags:
            msg += f' - flags=\'{flags}\''
        debug('msgid', msg)

    def print_command(self, mdpo_command, comment, original_command):
        msg = mdpo_command
        if comment:
            msg += f' - {comment}'
        if original_command and original_command != mdpo_command:
            msg += f' (original command: \'{original_command}\')'
        debug('command', msg)

    def print_enter_block(self, block, details):
        debug('enter_block', _block_msg(block, details))

    def print_leave_block(self, block, details):
        debug('leave_block', _block_msg(block, details))

    def print_enter_span(self, span, details):
        debug('enter_span', _block_msg(span, details))

    def print_leave_span(self, span, details):
        debug('leave_span', _block_msg(span, details))

    def print_text(self, block, text):
        debug('text', text)

    def print_link_reference(self, target, href, title):
        msg = f'target=\'{target}\''
        if href:
            msg += f' - href=\'{href}\''
        if title:
            msg += f' - title=\'{title}\''
        debug('link_reference', msg)

    return {
        'msgid': print_msgid,
        'enter_block': print_enter_block,
        'leave_block': print_leave_block,
        'enter_span': print_enter_span,
        'leave_span': print_leave_span,
        'text': print_text,
        'command': print_command,
        'link_reference': print_link_reference,
    }
