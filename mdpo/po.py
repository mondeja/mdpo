""".po files mdpo related stuff"""


def build_po_escaped_string(chars):
    return '\\' + chars[0]


def find_equal_without_consider_obsoletion(entry, entries):
    response = False
    for other in entries:
        if entry.__cmp__(other, compare_obsolete=False) == 0:
            response = True
            break
    return response
