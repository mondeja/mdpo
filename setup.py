#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
import sys

from setuptools import find_packages, setup, Command

PROJECT_NAME = 'md2po'
URL = 'https://github.com/mondeja/%s' % PROJECT_NAME
EMAIL = 'mondejar1994@gmail.com'
AUTHOR = 'Álvaro Mondéjar Rubio'
REQUIRES_PYTHON = '>=3'
REQUIRED = [
    'panflute>=1.12.5',
    'pypandoc>=1.5',
    'polib>=1.1.0',
]

TEST_EXTRAS = [
    'pytest>=6.0.1',
    'pytest-cov',
    'flake8',
    'flake8-print',
    'tox',
]
DOC_EXTRAS = [
    'Sphinx>=3.2.1',
    'sphinx-rtd-theme==0.4.3'
]
EXTRAS = {
    'dev': ['twine', 'bump2version'] + TEST_EXTRAS + DOC_EXTRAS,
    'test': TEST_EXTRAS,
    'docs': DOC_EXTRAS,
}

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

ABOUT = {}
INIT_FILEPATH = os.path.join(HERE, PROJECT_NAME, '__init__.py')
with io.open(INIT_FILEPATH, encoding='utf-8') as f:
    content = f.read()
    ABOUT['__title__'] = \
        re.search(r'__title__\s=\s[\'"]([^\'"]+)[\'"]', content).group(1)
    ABOUT['__version__'] = \
        re.search(r'__version__\s=\s[\'"]([^\'"]+)[\'"]', content).group(1)
    ABOUT['__description__'] = \
        re.search(r'__description__\s=\s[\'"]([^\'"]+)[\'"]', content).group(1)


class UploadCommand(Command):
    'Support setup.py upload.'

    description = 'Build and publish the package.'
    user_options = [
        ('test', None, 'Specify if you want to test your upload to Pypi.'),
    ]

    @staticmethod
    def status(s):
        'Prints things in bold.'
        sys.stdout.write('\033[1m{0}\033[0m\n'.format(s))

    def initialize_options(self):
        self.test = None

    def finalize_options(self):
        pass

    def run(self):
        from shutil import rmtree
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(
            sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        cmd = 'twine upload%s dist/*' % (
            ' --repository-url https://test.pypi.org/legacy/' if self.test
            else ''
        )
        os.system(cmd)
        sys.exit()


setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],
    description=ABOUT['__version__'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    project_urls={
        'Documentation': 'https://Python-Markdown.github.io/',
        'GitHub Project': 'https://github.com/mondeja/md2po',
        'Issue Tracker': 'https://github.com/mondeja/md2po/issues'
    },
    entry_points={
        'console_scripts': [
            '%s = %s.__main__:run' % (PROJECT_NAME, PROJECT_NAME),
        ],
    },
    packages=find_packages(exclude=['test']),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='BSD License',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing',
        # 'Topic :: Text Processing :: Markup :: Markdown',
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)
