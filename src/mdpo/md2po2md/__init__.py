"""Markdown to PO file to Markdown translator."""

import glob
import os

from mdpo.md2po import Md2Po
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.po import (
    check_empty_msgstrs_in_filepaths,
    check_fuzzy_entries_in_filepaths,
    check_obsolete_entries_in_filepaths,
)
from mdpo.po2md import Po2Md


def markdown_to_pofile_to_markdown(
    langs,
    input_paths_glob,
    output_paths_schema,
    extensions=DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
    command_aliases=None,
    location=True,
    debug=False,
    po_wrapwidth=78,
    md_wrapwidth=80,
    po_encoding=None,
    md_encoding=None,
    include_codeblocks=False,
    md2po_kwargs=None,
    po2md_kwargs=None,
    _check_saved_files_changed=False,
    no_obsolete=False,
    no_fuzzy=False,
    no_empty_msgstr=False,
):
    """Translate a set of Markdown files using PO files.

    Args:
        langs (list): List of languages used to build the output directories.
        input_paths_glob (str): Glob covering Markdown files to translate.
        output_paths_schema (str): Path schema for outputs, built using
            placeholders. There is a mandatory placeholder for languages:
            ``{lang}``; and one optional for output basename: ``{basename}``.
            For example, for the schema ``locale/{lang}``, the languages
            ``['es', 'fr']`` and a ``README.md`` as input, the next files will
            be written:

            * ``locale/es/README.po``
            * ``locale/es/README.md``
            * ``locale/fr/README.po``
            * ``locale/fr/README.md``

            Note that you can omit ``{basename}``, specifying a directory for
            each language with ``locale/{lang}`` for this example.
            Unexistent directories and files will be created, so you don't
            have to prepare the output directories before the execution.
        extensions (list): md4c extensions used to parse markdown content,
            formatted as a list of 'pymd4c' keyword arguments. You can see all
            available at `pymd4c documentation <https://pymd4c.dcpx.org/
            api.html#option-flags>`_.
        command_aliases (dict): Mapping of aliases to use custom mdpo command
            names in comments. The ``mdpo-`` prefix in command names resolution
            is optional. For example, if you want to use ``<!-- mdpo-on -->``
            instead of ``<!-- mdpo-enable -->``, you can pass the dictionaries
            ``{"mdpo-on": "mdpo-enable"}`` or ``{"mdpo-on": "enable"}`` to this
            parameter.
        location (bool): Store references of top-level blocks in which are
            found the messages in PO file ``#: reference`` comments.
        debug (bool): Add events displaying all parsed elements in the
            extraction process.
        po_wrapwidth (int): Maximum width for PO files.
        md_wrapwidth (int): Maximum width for produced Markdown contents, when
            possible.
        po_encoding (str): PO files encoding.
        md_encoding (str): Markdown files encoding.
        include_codeblocks (bool): Include codeblocks in the extraction process.
        md2po_kwargs (dict): Additional optional arguments passed to
            ``markdown_to_pofile`` function.
        po2md_kwargs (dict): Additional optional arguments passed to
            ``pofile_to_markdown`` function.
        no_obsolete (bool): If ``True``, check for obsolete entries in PO files.
        no_fuzzy (bool): If ``True``, check for fuzzy entries in PO files.
        no_empty_msgstr (bool): If ``True``, check for empty ``msgstr`` entries.
    """
    if '{lang}' not in output_paths_schema:
        raise ValueError(
            "You must pass the replacer '{lang}' inside the argument"
            " 'output_paths_schema'.",
        )

    try:
        input_paths_glob_ = glob.glob(input_paths_glob)
    except Exception as err:
        if (
            err.__module__ in ['re', 'sre_constants']
            and err.__class__.__name__ == 'error'
        ):
            # some strings like '[s-m]' will produce
            raise FileNotFoundError(
                "The argument 'input_paths_glob' must be a valid glob or file"
                ' path.',
            ) from None
        raise err
    else:
        if not input_paths_glob_:
            raise FileNotFoundError(
                f"The glob '{input_paths_glob}' does not match any file.",
            )

    _saved_files_changed = None if not _check_saved_files_changed else False
    obsoletes = []
    fuzzies = []
    empties = []

    for filepath in input_paths_glob_:
        for lang in langs:
            md_ext = os.path.splitext(filepath)[-1]

            file_basename = os.path.splitext(os.path.basename(filepath))[0]

            format_kwargs = {'lang': lang}
            if '{basename}' in output_paths_schema:
                format_kwargs['basename'] = file_basename
            po_filepath = output_paths_schema.format(**format_kwargs)

            po_basename = os.path.basename(po_filepath)
            po_dirpath = (
                os.path.dirname(po_filepath)
                if (po_basename.count('.') or file_basename == po_basename)
                else po_filepath
            )

            os.makedirs(os.path.abspath(po_dirpath), exist_ok=True)
            if os.path.isdir(po_filepath):
                po_filepath = os.path.join(
                    po_filepath.rstrip(os.sep),
                    f'{os.path.basename(filepath)}.po',
                )
            if not po_filepath.endswith('.po'):
                po_filepath += '.po'

            format_kwargs['ext'] = md_ext.lstrip('.')
            md_filepath = output_paths_schema.format(**format_kwargs)
            if os.path.isdir(md_filepath):
                md_filepath = os.path.join(
                    md_filepath.rstrip(os.sep),
                    os.path.basename(filepath),
                )

            # md2po
            md2po = Md2Po(
                filepath,
                extensions=extensions,
                command_aliases=command_aliases,
                debug=debug,
                location=location,
                wrapwidth=po_wrapwidth,
                include_codeblocks=include_codeblocks,
                _check_saved_files_changed=_check_saved_files_changed,
                **(md2po_kwargs or {}),
            )
            md2po.extract(
                save=True,
                po_filepath=po_filepath,
                po_encoding=po_encoding,
                md_encoding=md_encoding,
            )
            if _check_saved_files_changed and _saved_files_changed is False:
                _saved_files_changed = md2po._saved_files_changed

            # po2md
            po2md = Po2Md(
                [po_filepath],
                command_aliases=command_aliases,
                debug=debug,
                po_encoding=po_encoding,
                wrapwidth=md_wrapwidth,
                _check_saved_files_changed=_check_saved_files_changed,
                **(po2md_kwargs or {}),
            )
            po2md.translate(
                filepath,
                save=md_filepath,
                md_encoding=md_encoding,
            )
            if _check_saved_files_changed and _saved_files_changed is False:
                _saved_files_changed = po2md._saved_files_changed

            if no_obsolete:
                obsoletes.extend(check_obsolete_entries_in_filepaths(
                    [po_filepath],
                ))

            if no_fuzzy:
                fuzzies.extend(
                    check_fuzzy_entries_in_filepaths([po_filepath]),
                )

            if no_empty_msgstr:
                empties.extend(
                    check_empty_msgstrs_in_filepaths([po_filepath]),
                )

    return (_saved_files_changed, obsoletes, fuzzies, empties)
