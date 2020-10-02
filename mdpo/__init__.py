"""mdpo package"""

from mdpo.md2po import markdown_to_pofile
from mdpo.po2md import pofile_to_markdown


__version__ = '0.2.3'
__version_info__ = tuple([int(i) for i in __version__.split('.')])
__title__ = 'mdpo'
__description__ = ('Utilities to translate Markdown files using `.po`'
                   ' files.')
__all__ = ("markdown_to_pofile", "pofile_to_markdown")