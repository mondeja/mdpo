"""Compatibilities for different versions of Python."""

import sys
import tempfile


if sys.version_info < (3, 10):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


def instanciate_po_library(po_library='polib'):
    if po_library == 'polib':
        import polib

        def create_pofile(filepath, encoding='utf-8', wrapwidth=80, **kwargs):
            pofile_kwargs = (
                {'autodetect_encoding': False, 'encoding': encoding}
                if encoding else {}
            )
            pofile_kwargs.update(kwargs)
            return polib.pofile(
                filepath,
                wrapwidth=wrapwidth,
                **pofile_kwargs,
            )

        def pofile_to_string(pofile, **kwargs):  # noqa: U100
            return pofile.__unicode__()

        def create_pofile_entry(msgid, msgstr, tcomment, msgctxt, fuzzy):
            return polib.POEntry(
                msgid=msgid,
                msgstr=msgstr,
                comment=tcomment,
                msgctxt=msgctxt,
                flags=[] if not fuzzy else ['fuzzy'],
            )

        def append_entry_to_pofile(pofile, entry):
            if entry not in pofile:
                pofile.append(entry)

        def is_polib():
            return True

        def set_entry_attr(entry, attr, value):
            setattr(entry, attr, value)

        def get_entry_attr(entry, attr):
            return getattr(entry, attr)

        def save_pofile(pofile, po_filepath, mo_filepath=None):
            pofile.save(fpath=po_filepath)
            if mo_filepath:
                pofile.save_as_mofile(mo_filepath)

        def save_mofile(pofile, mo_filepath):
            pofile.save_as_mofile(mo_filepath)

    else:

        import os
        gettextpo_dist_dir = os.path.join(
            os.path.dirname(__file__), '../pygettextpo/dist')
        if gettextpo_dist_dir not in sys.path:
            sys.path.insert(0, gettextpo_dist_dir)

        import gettextpo

        def create_pofile(
            filepath,
            encoding='utf-8',  # noqa: U100
            wrapwidth=80,  # noqa: U100
            **kwargs,  # noqa: U100
        ):
            pofile_kwargs = {'filename': filepath} if filepath else {}
            return gettextpo.PoFile(**pofile_kwargs)

        def pofile_to_string(pofile, **kwargs):
            with tempfile.NamedTemporaryFile(
                mode='w+', encoding=kwargs.get('encoding', 'utf-8'),
            ) as f:
                pofile.write(f.name)
                output = f.read()
            return output

        def create_pofile_entry(msgid, msgstr, tcomment, msgctxt, fuzzy):
            entry = gettextpo.PoMessage()
            entry.set_msgid(msgid.encode('utf-8'))
            entry.set_msgstr(msgstr.encode('utf-8'))
            if tcomment:
                entry.set_comments(tcomment.encode('utf-8'))
            if msgctxt:
                entry.set_msgctxt(msgctxt.encode('utf-8'))
            return entry

        def append_entry_to_pofile(pofile, entry):
            poiter = iter(pofile)
            poiter.insert(entry)

        def is_polib():
            return False

        def get_entry_attr(entry, attr):
            ret = getattr(entry, attr)
            return ret.decode('utf-8') if ret else ret

        def set_entry_attr(entry, attr, value):
            getattr(entry, f'set_{attr}')(value.encode('utf-8'))

        def save_pofile(pofile, po_filepath):
            pofile.write(po_filepath)

        def save_mofile(pofile, mo_filepath):
            polib.pofile(str(pofile)).save_as_mofile(mo_filepath)

    return type(
        'PoLibraryImplementation', (), {
            'is_polib': is_polib,
            'create_pofile': create_pofile,
            'pofile_to_string': pofile_to_string,
            'create_pofile_entry': create_pofile_entry,
            'append_entry_to_pofile': append_entry_to_pofile,
            'get_entry_attr': get_entry_attr,
            'set_entry_attr': set_entry_attr,
            'save_pofile': save_pofile,
            'save_mofile': save_mofile,
        },
    )


__all__ = (
    'importlib_metadata',
    'instanciate_po_library',
)
