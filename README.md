# mdpo

<!-- mdpo-disable -->

[![PyPI][pypi-image]][pypi-link]
[![PyPI Python versions][pypi-versions-image]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
[![Documentation status][doc-image]][doc-link]

<!-- mdpo-enable -->

Utilities for Markdown files translation using `.po` files. Fully complies
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

#### Specifying in `requirements.txt`

```ini
-e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c
mdpo
```

## [Documentation][doc-link]

---

<!-- mdpo-disable -->

> You can see the README introduction translated to other languages using the
> library from [this script][process-locales-script-link]:
>
> - [Spanish][spanish-readme-link]

<!-- mdpo-enable -->

[pypi-image]: https://img.shields.io/pypi/v/mdpo
[pypi-link]: https://pypi.org/project/mdpo/
[pypi-versions-image]: https://img.shields.io/pypi/pyversions/mdpo?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image]: https://img.shields.io/pypi/l/mdpo?color=light-green
[license-link]: https://github.com/mondeja/mdpo/blob/master/LICENSE
[tests-image]: https://img.shields.io/travis/mondeja/mdpo?label=tests
[tests-link]: https://travis-ci.com/github/mondeja/mdpo
[coverage-image]: https://coveralls.io/repos/github/mondeja/mdpo/badge.svg
[coverage-link]: https://coveralls.io/github/mondeja/mdpo
[doc-image]: https://readthedocs.org/projects/mdpo/badge/?version=latest
[doc-link]: https://mdpo.readthedocs.io/en/latest/
[pofile-doc-link]: https://polib.readthedocs.io/en/latest/api.html#polib.POFile
[polib-doc-link]: https://polib.readthedocs.io/en/latest
[pymd4c-link]: https://github.com/dominickpastore/pymd4c
[pymd4c-build-from-source-link]: https://github.com/dominickpastore/pymd4c#build-and-install-from-source
[mdpo2html-link]: https://github.com/mondeja/mdpo2html
[commonmark-spec-link]: https://spec.commonmark.org/0.29
[process-locales-script-link]: https://github.com/mondeja/mdpo/blob/master/process-locales.py
[spanish-readme-link]: https://github.com/mondeja/mdpo/blob/master/locale/readme/es.md
