# md2po (WIP)

[![PyPI](https://img.shields.io/pypi/v/md2po)](https://pypi.org/project/md2po/) [![PyPI versions](https://img.shields.io/pypi/pyversions/md2po)](https://pypi.org/project/md2po/) [![Tests](https://img.shields.io/travis/mondeja/md2po?label=tests)](https://travis-ci.com/github/mondeja/md2po) [![Coverage Status](https://coveralls.io/repos/github/mondeja/md2po/badge.svg)](https://coveralls.io/github/mondeja/md2po)

Markdown to `.po` file messages extractor. Extract the contents of a set of Markdown files to one `.po` file.

> I've written only those functionalities that have needed, so if you want to see more added to this package, [send a pull request](https://github.com/mondeja/md2po/pulls) or [open an issue](https://github.com/mondeja/md2po/issues/new) with a minimal example.

## Install

You must install Pandoc 2.5 first:

```bash
pip install pypandoc
python -c "import pypandoc as p;p.download_pandoc(version='2.5', delete_installer=True);"
```

...and then:

```bash
pip install md2po
```

## Quickstart

Create a new `.po` file extracting strings from markdown files:

```python
from md2po import markdown_to_pofile

pofile = markdown_to_pofile('doc/src/**/**.md', ignore=['todo.md', 'changelog.md'])
pofile.save('locale/doc.po')

# in one line
markdown_to_pofile('doc/src/**/**.md', ignore=['todo.md', 'changelog.md']).save('locale/doc.po')
```

The function `markdown_to_pofile` returns a [POFile](https://polib.readthedocs.io/en/latest/api.html#polib.POFile) instance from the library [polib](https://polib.readthedocs.io/en/latest). If you indicates an existent `.po` file path for `po_filepath` optional argument, the new content will be merged into the file:

```python
markdown_to_pofile('doc/src/**/**.md',
                   ignore=['todo.md', 'changelog.md'],
                   po_filepath='locale/doc.po',
                   save=True)
```

If you doesn't pass the argument `save` to `True`, you will get a new [POFile](https://polib.readthedocs.io/en/latest/api.html#polib.POFile) instance with new and old message strings merged.

Also, you can pass Markdown content as a string to extract messages from it:

```python
>>> from md2po import markdown_to_pofile

>>> md_content = '''# Header
... 
... Some text
... '''
>>>
>>> pofile = markdown_to_pofile(md_content))
>>> print(pofile)
#
msgid ""
msgstr ""

msgid "Header"
msgstr ""

msgid "Some text"
msgstr ""

```

## Plain vs markup text mode

If you pass the argument `plaintext` as `False`, the converter does not will remove some text markup (like `inline code`, **bold text** and other elements). These characters can be used, for example as separators translating other markup formats like HTML or to indicate translators that some strings must not be translated. The conversion will follow next correspondences:

```
Markdown --------------------------------> .po file text

`inline code` ---------------------------> `inline code`
``inline code ` with backtick`` ---------> `inline code \\` with backtick`
**bold text** ---------------------------> **bold text**
*italic text* ---------------------------> *italic text*
<simple/link> ---------------------------> `[simple link]`
paragraph with \* asterisk --------------> paragraph with \\* asterisk
```

## Known limitations

- Tables are not supported with `Pandoc 2.10` (and maybe some other recent versions) because [panflute](https://github.com/sergiocorreia/panflute) dependency does not support tables with captions (pandoc >= 2.10), as has been addressed in [panflute/issues/#142](https://github.com/sergiocorreia/panflute/issues/142).
