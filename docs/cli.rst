***********************
Command line interfaces
***********************

mdpo installation includes two command line interfaces:

* ``md2po`` is used to dump strings from Markdown files into pofiles as msgids.
* ``po2md`` is used to produce a translated Markdown file from a source Markdown
  file and a pofile with extracted msgids and translated msgstrs.

md2po
=====

.. argparse::
   :module: mdpo.md2po.__main__
   :func: build_parser
   :prog: md2po
   :nodefault:


po2md
=====

.. argparse::
   :module: mdpo.po2md.__main__
   :func: build_parser
   :prog: po2md
   :nodefault:
