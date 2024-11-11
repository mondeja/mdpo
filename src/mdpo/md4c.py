"""md4c related stuff for mdpo."""


#: :list: `md4c parser <https://github.com/mity/md4c>`_ extensions
#: used by default on :doc:`md2po </dev/reference/mdpo.md2po>` and
#: :doc:`po2md </dev/reference/mdpo.po2md>` implementations.


DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS = [
    'collapse_whitespace',
    'tables',
    'strikethrough',
    'tasklists',
    'latex_math_spans',
    'wikilinks',
]

#: :dict: mapping from `pymd4c <https://pymd4c.dcpx.org/>`_
#: block type values to block readable names
READABLE_BLOCK_NAMES = {
    1: 'quote',
    2: 'unordered list',
    3: 'ordered list',
    6: 'header',
    7: 'code',
    8: 'html',
    9: 'paragraph',
    10: 'table',
}
