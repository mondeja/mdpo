""".po files mdpo related stuff"""


def build_po_escaped_string(chars):
    return '\\' + chars[0]


def find_entry_in_entries(entry, entries, **kwargs):
    response = None
    for other in entries:
        if entry.__cmp__(other, **kwargs) == 0:
            response = other
            break
    return response
