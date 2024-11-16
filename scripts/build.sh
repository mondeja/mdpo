#!/bin/sh

set -ex

rm -rf build dist
export TMPDIR=/var/tmp/
export PYI_LOG_LEVEL=WARN

pyinstaller -y --onefile \
    --optimize 2 \
    --name md2po \
    --copy-metadata mdpo \
    src/mdpo/md2po/__main__.py &
pyinstaller -y --onefile \
    --optimize 2 \
    --name po2md \
    --copy-metadata mdpo \
    src/mdpo/po2md/__main__.py &
pyinstaller -y --onefile \
    --optimize 2 \
    --name md2po2md \
    --copy-metadata mdpo \
    src/mdpo/md2po2md/__main__.py &
pyinstaller -y --onefile \
    --optimize 2 \
    --name mdpo2html \
    --copy-metadata mdpo \
    src/mdpo/mdpo2html/__main__.py
