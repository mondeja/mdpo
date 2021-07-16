"""Markdown to PO file to Markdown translator."""

import os

from mdpo.io import to_glob_or_content
from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS
from mdpo.po2md import pofile_to_markdown


def markdown_to_pofile_to_markdown(
    langs,
    input_paths_glob,
    output_paths_schema,
    extensions=DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS,
    command_aliases={},
    debug=False,
    md2po_kwargs={},
    po2md_kwargs={},
):
    """Translate a set of Markdown files using PO files.

    Args:
        langs (list): List of languages used to build the output directories.
        input_paths_glob (str): Glob covering Markdown files to translate.
        output_paths_schema (str): Path schema for outputs, built using
            placeholders. There is a mandatory placeholder for languages:
            ``{lang}``; and two for the output basename and extension:
            ``{basename}`` and ``{ext}``.
            For example, for the schema ``locale/{lang}/{basename}.{ext}``,
            the languages ``['es', 'fr']`` and a ``README.md`` as input,
            the next files will be written:

            * ``locale/es/README.po``
            * ``locale/es/README.md``
            * ``locale/fr/README.po``
            * ``locale/fr/README.md``

            You can also omit ``{basename}`` and ``{ext}``, specifying a
            directory for each language with ``locale/{lang}`` for this
            example.
            Unexistent directories and files will be created, so you don't
            have to prepare the output directories before the execution.
        extensions (list): md4c extensions used to parse markdown content,
            formatted as a list of 'pymd4c' keyword arguments. You can see all
            available at `pymd4c repository <https://github.com/dominickpastore
            /pymd4c#parser-option-flags>`_.
        command_aliases (dict): Mapping of aliases to use custom mdpo command
            names in comments. The ``mdpo-`` prefix in command names resolution
            is optional. For example, if you want to use ``<!-- mdpo-on -->``
            instead of ``<!-- mdpo-enable -->``, you can pass the dictionaries
            ``{"mdpo-on": "mdpo-enable"}`` or ``{"mdpo-on": "enable"}`` to this
            parameter.
        debug (bool): Add events displaying all parsed elements in the
            extraction process.
        md2po_kwargs (dict): Additional optional arguments passed to
            ``markdown_to_pofile`` function.
        po2md_kwargs (dict): Additional optional arguments passed to
            ``pofile_to_markdown`` function.
    """
    if '{lang}' not in output_paths_schema:
        raise ValueError(
            "You must pass the replacer '{lang}' inside the argument"
            " 'output_paths_schema'.",
        )

    is_glob, input_paths_glob = to_glob_or_content(input_paths_glob)
    if not is_glob:
        raise ValueError(
            "The argument 'input_paths_glob' must be a valid glob or file"
            ' path.',
        )

    for filepath in input_paths_glob:
        for lang in langs:
            md_ext = os.path.splitext(filepath)[-1]

            format_kwargs = {'lang': lang}
            if '{basename}' in output_paths_schema:
                format_kwargs['basename'] = os.path.basename(filepath)
            if '{ext}' in output_paths_schema:
                format_kwargs['ext'] = 'po'
            po_filepath = output_paths_schema.format(**format_kwargs)

            po_dirpath = (
                os.path.dirname(po_filepath)
                if '.' in os.path.basename(po_filepath) else po_filepath
            )

            os.makedirs(os.path.abspath(po_dirpath), exist_ok=True)
            if os.path.isdir(po_filepath):
                po_filepath = (
                    po_filepath.rstrip(os.sep) + os.sep +
                    os.path.basename(filepath) + '.po'
                )

            format_kwargs['ext'] = md_ext.lstrip('.')
            md_filepath = output_paths_schema.format(**format_kwargs)
            if os.path.isdir(md_filepath):
                md_filepath = (
                    md_filepath.rstrip(os.sep) + os.sep +
                    os.path.basename(filepath)
                )

            markdown_to_pofile(
                filepath,
                save=True,
                po_filepath=po_filepath,
                extensions=extensions,
                command_aliases=command_aliases,
                debug=debug,
                **md2po_kwargs,
            )

            pofile_to_markdown(
                filepath,
                [po_filepath],
                save=md_filepath,
                command_aliases=command_aliases,
                debug=debug,
                **po2md_kwargs,
            )
