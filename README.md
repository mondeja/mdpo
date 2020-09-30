# mdpo

[![PyPI][pypi-image]][pypi-link]
[![PyPI Python versions][pypi-versions-image]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
[![Documentation status][doc-image]][doc-link]

Set of utilities to translate Markdown files using `.po` files. Fully complies
 with [CommonMark Specification][commonmark-spec-link], supporting some
 additional features.

## Install

You need to compile [md4c](https://github.com/mity/md4c/wiki/Building-MD4C)
before install, and then:

### Linux

```bash
pip install \
  -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c \
  && pip install mdpo
```

#### Specifying in requirements

```ini
-e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c
mdpo
```

## [Documentation](doc-link)

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
[pofile-doc-link]: https://polib.readthedocs.io/en/latest/api.html#polib.POFile
[polib-doc-link]: https://polib.readthedocs.io/en/latest
[pymd4c-link]: https://github.com/dominickpastore/pymd4c
[pymd4c-build-from-source-link]: https://github.com/dominickpastore/pymd4c#build-and-install-from-source
[mdpo2html-link]: https://github.com/mondeja/mdpo2html
[commonmark-spec-link]: https://spec.commonmark.org/0.29
