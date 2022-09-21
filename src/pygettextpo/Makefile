# Copyright Canonical Ltd.  This software is licensed under the GNU
# Affero General Public License version 3 (see the file LICENSE).

PYTHON = python
PYDOC = pydoc

all: clean gettextpo.so gettextpo.html sdist wheel

check: clean ext
	$(PYTHON) test_gettextpo.py -v

clean:
	rm -rf build dist gettextpo*.so gettextpo.html pygettextpo.egg-info

docs: ext
	cd dist
	$(PYDOC) -w gettextpo

ext:
	$(PYTHON) setup.py build_ext --build-lib dist

sdist: ext
	$(PYTHON) setup.py sdist

wheel: ext
	$(PYTHON) -m pip wheel . --no-deps -w dist/

.PHONY: all check clean


# generate wheel
# python -m pip wheel --wheel-dir=/tmp/g .

# install wheel
# python3 -m pip install --no-index --find-links=/tmp/g pygettextpo
