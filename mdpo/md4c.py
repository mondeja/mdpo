"""md4c related stuff for mdpo"""

import md4c


DEFAULT_MD4C_FLAGS = ('MD_FLAG_COLLAPSEWHITESPACE|'
                      'MD_FLAG_TABLES|'
                      'MD_FLAG_STRIKETHROUGH|'
                      'MD_FLAG_TASKLISTS|'
                      'MD_FLAG_LATEXMATHSPANS|'
                      'MD_FLAG_WIKILINKS')


def parse_md4c_flags_string(flags_string):
    modes = {
        "strikethrough": False,
        "latexmathspans": False,
        "wikilinks": False,
        "underline": False,  # unactive by default
    }
    flags_string = flags_string.replace('+', '|').replace(' ', '')
    flags_list = []
    for flag in flags_string.split('|'):
        if not hasattr(md4c, flag):
            continue
        md4c_attr = getattr(md4c, flag)
        flags_list.append(md4c_attr)
        if md4c_attr == md4c.MD_FLAG_STRIKETHROUGH:
            modes["strikethrough"] = True
        elif md4c_attr == md4c.MD_FLAG_LATEXMATHSPANS:
            modes["latexmathspans"] = True
        elif md4c_attr == md4c.MD_FLAG_WIKILINKS:
            modes['wikilinks'] = True
        elif md4c_attr == md4c.MD_FLAG_UNDERLINE:
            modes['underline'] = True
    return (sum(flags_list), modes)
