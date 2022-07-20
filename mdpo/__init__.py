"""mdpo package."""

func_package_map = {
    'markdown_pofile_to_html': 'mdpo2html',
    'markdown_to_pofile': 'md2po',
    'markdown_to_pofile_to_markdown': 'md2po2md',
    'pofile_to_markdown': 'po2md',
}

__all__ = list(func_package_map.keys())


def __getattr__(name):
    """Implement PEP 562 to avoid uneeded imports in CLIs."""
    import importlib

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
