# md2po

[![PyPI][pypi-image]][pypi-link]
[![PyPI Python versions][pypi-versions-image]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
[![Documentation status][doc-image]][doc-link]


Library and command line interface to extract contents of a set of Markdown files and save into `.po` files. Is like a tiny xgettext utility for Markdown files written in Python.

> If you want a solution to replace your extracted strings into a HTML file you can use [md2po-html-replacer](https://github.com/mondeja/md2po-html-replacer).

## Install

You must install Pandoc<=2.9 first:

```bash
pip install pypandoc
python -c "import pypandoc as p;p.download_pandoc(version='2.9', delete_installer=True);"
```

...and then:

```bash
pip install md2po
```

## Quickstart

### Basic usage

Create a new `.po` file extracting strings from markdown files:

```python
from md2po import markdown_to_pofile

pofile = markdown_to_pofile('doc/src/**/**.md', ignore=['todo.md', 'changelog.md'])
pofile.save('locale/doc.po')

# in one line
markdown_to_pofile('doc/src/**/**.md',
                   ignore=['todo.md', 'changelog.md'],
                   po_filepath='locale/doc.po',
                   save=True)
```

> The function `markdown_to_pofile` returns a [POFile](https://polib.readthedocs.io/en/latest/api.html#polib.POFile) instance from the library [polib](https://polib.readthedocs.io/en/latest). If you indicates an existent `.po` file path for `po_filepath` optional argument, the new content will be merged into that file:

If you doesn't pass the argument `save` to `True`, you will get a new [POFile](https://polib.readthedocs.io/en/latest/api.html#polib.POFile) instance with new and old message strings merged.

Also, you can pass Markdown content as a string to extract messages from it:

```python
>>> from md2po import markdown_to_pofile

>>> md_content = '''# Header
...
... Some text
... '''
>>>
>>> pofile = markdown_to_pofile(md_content)
>>> print(pofile)
#
msgid ""
msgstr ""

msgid "Header"
msgstr ""

msgid "Some text"
msgstr ""
```

### Disabling extraction

You can disable and enable the extraction of certain strings using next HTML commments:

- `<!-- md2po-disable-next-line -->`
- `<!-- md2po-disable -->`
- `<!-- md2po-enable -->`
- `<!-- md2po-enable-next-line -->`

For example:
```python
>>> from md2po import markdown_to_pofile

>>> md_content = '''# Header
...
... This will be included
...
... <!-- md2po-disable-next-line -->
... This will be ignored.
...
... This will be included also.
... '''
>>>
>>> pofile = markdown_to_pofile(md_content)
>>> print(pofile)
#
msgid ""
msgstr ""

msgid "This will be included."
msgstr ""

msgid "This will be included also."
msgstr ""
```

## Command line interface

Installation includes a command line utility named `md2po`:

```bash
md2po -f "locale/doc.po" -s -i "todo.md,changelog.md" "doc/src/**/**.md"
```


## Documentation
For a full list of parameters supported [see the documentation on ReadTheDocs][doc-link].


## Known limitations

- Tables are not supported with `Pandoc v2.10` because [panflute](https://github.com/sergiocorreia/panflute) dependency does not support tables with captions (pandoc >= 2.10), as has been addressed in [panflute/issues/#142](https://github.com/sergiocorreia/panflute/issues/142).

[pypi-image]: https://img.shields.io/pypi/v/md2po
[pypi-link]: https://pypi.org/project/md2po/
[pypi-versions-image]: https://img.shields.io/pypi/pyversions/md2po?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image]: https://img.shields.io/pypi/l/md2po?color=light-green
[license-link]: https://github.com/mondeja/md2po/blob/master/LICENSE
[tests-image]: https://img.shields.io/travis/mondeja/md2po?label=tests
[tests-link]: https://travis-ci.com/github/mondeja/md2po
[coverage-image]: https://coveralls.io/repos/github/mondeja/md2po/badge.svg
[coverage-link]: https://coveralls.io/github/mondeja/md2po
[doc-image]: https://readthedocs.org/projects/md2po/badge/?version=latest
[doc-link]: https://md2po.readthedocs.io/en/latest/
