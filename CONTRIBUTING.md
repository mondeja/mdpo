# Contributing

## Linux

To setup your development environment, run:

```bash
python3 -m virtualenv venv
. venv/bin/activate
python -m pip install -e .[dev]
pre-commit install
python -c "import os,pypandoc as p;p.download_pandoc(version='2.9', delete_installer=True, targetfolder=os.path.abspath(os.path.join('venv', 'bin')));"
```
