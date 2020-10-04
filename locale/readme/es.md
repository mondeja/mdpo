# mdpo

Utilidades para traducción de archivos Markdown usando `.po` files. Cumple
comepletamente con la [especificación
CommonMark](https://spec.commonmark.org/0.29), soportando algunas
características adicionales.

## Instalación

Necesitas compilar [md4c](https://github.com/mity/md4c/wiki/Building-MD4C) antes
de instalar, y entonces:

### Linux

```bash
pip install \
  -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c \
  && pip install mdpo
```

#### Especificando en `requirements.txt`

```ini
-e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c
mdpo
```

## [Documentación](https://mdpo.readthedocs.io/en/latest/)
