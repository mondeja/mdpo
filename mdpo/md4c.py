"""md4c related stuff for mdpo."""


#: :list: `md4c parser <https://github.com/mity/md4c>`_ extensions used as
#: default by :ref:`md2po<md2po-init>` and :ref:`po2md<po2md-init>`
#: implementations.
DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS = [
    'collapse_whitespace',
    'tables',
    'strikethrough',
    'tasklists',
    'latex_math_spans',
    'wikilinks',
]

#: :dict: mapping from `pymd4c <https://github.com/dominickpastore/pymd4c>`_
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
