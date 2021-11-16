"""mdpo package."""

__description__ = ('Markdown files translation using PO files.')
__title__ = 'mdpo'
__version__ = '0.3.80'
__all__ = [
    '__description__',
    '__title__',
    '__version__',
]


def __getattr__(name):
    """Implements PEP 562 to avoid uneeded imports in CLIs."""
    import importlib
    func_package_map = {
        'markdown_pofile_to_html': 'mdpo2html',
        'markdown_to_pofile': 'md2po',
        'markdown_to_pofile_to_markdown': 'md2po2md',
        'pofile_to_markdown': 'po2md',
    }
    try:
        return getattr(
            importlib.import_module(f'mdpo.{func_package_map[name]}'),
            name,
        )
    except KeyError:
        raise ImportError(
            f'cannot import name \'{name}\' from \'mdpo\' ({__file__})',
            name=name,
            path='mdpo',
        ) from None


def __dir__():
    return __all__ + [
        'markdown_pofile_to_html',
        'markdown_to_pofile',
        'markdown_to_pofile_to_markdown',
        'pofile_to_markdown',
    ]
