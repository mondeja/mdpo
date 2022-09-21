#!/usr/bin/env python
#
# Copyright Canonical Ltd.  This software is licensed under the GNU
# Affero General Public License version 3 (see the file LICENSE).

from setuptools import Extension, setup


gettextpo = Extension(
    'gettextpo',
    ['gettextpo.c'],
    libraries=['gettextpo'],
    language='c',
)

setup(
    name='pygettextpo',
    version='0.2',
    author='Canonical Ltd.',
    author_email='lazr-developers@lists.launchpad.net',
    description='A binding for the libgettext-po library',
    url='https://launchpad.net/pygettextpo',
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    ext_modules=[gettextpo],
)
