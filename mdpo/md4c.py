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
