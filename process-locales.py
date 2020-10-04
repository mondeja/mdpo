#!/usr/bin/env python

import os

from mdpo import markdown_to_pofile, pofile_to_markdown

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOCALE_DIR = os.path.join(BASE_DIR, 'locale')
LOCALE_README_DIR = os.path.join(LOCALE_DIR, 'readme')

LANGUAGES = ['es']


def process_readme_locales():
    if not os.path.exists(LOCALE_README_DIR):
        os.mkdir(LOCALE_README_DIR)

    source_readme_filepath = os.path.join(BASE_DIR, 'README.md')

    for language in LANGUAGES:
        po_filepath = os.path.join(LOCALE_README_DIR, '%s.po' % language)
        readme_filepath = os.path.join(LOCALE_README_DIR, '%s.md' % language)

        markdown_to_pofile(source_readme_filepath,
                           save=True, po_filepath=po_filepath)
        pofile_to_markdown(source_readme_filepath, po_filepath,
                           save=readme_filepath)


def main():
    if not os.path.exists(LOCALE_DIR):
        os.mkdir(LOCALE_DIR)

    process_readme_locales()


if __name__ == '__main__':
    main()
