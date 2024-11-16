#!/bin/sh

set -ex

rm -rf build dist
export TMPDIR=/var/tmp/
export PYI_LOG_LEVEL=WARN

mdpo() {
    pyinstaller -y --onefile \
        --optimize 2 \
        --name md2po \
        --copy-metadata mdpo \
        src/mdpo/md2po/__main__.py
}

po2md() {
    pyinstaller -y --onefile \
        --optimize 2 \
        --name po2md \
        --copy-metadata mdpo \
        src/mdpo/po2md/__main__.py
}

md2po2md() {
    pyinstaller -y --onefile \
        --optimize 2 \
        --name md2po2md \
        --copy-metadata mdpo \
        src/mdpo/md2po2md/__main__.py
}

mdpo2html() {
    pyinstaller -y --onefile \
        --optimize 2 \
        --name mdpo2html \
        --copy-metadata mdpo \
        src/mdpo/mdpo2html/__main__.py
}

# Parallel build on Linux
if [ $(uname) = "Linux" ]; then
    mdpo &
    po2md &
    md2po2md &
    mdpo2html
else
    mdpo
    po2md
    md2po2md
    mdpo2html
fi
