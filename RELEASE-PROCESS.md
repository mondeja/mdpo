# Release process

1. `bump2version <change> --allow-dirty`
2. `git commit`
3. `git push`
4. `git tag -a v$(python3 -c 'import mdpo;print(mdpo.__version__)')`
5. Create release manually in Github including changes.
6. Upload to PyPI with `python3 setup.py upload`