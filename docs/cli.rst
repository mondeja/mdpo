***********************
Command line interfaces
***********************

mdpo installation includes two command line interfaces:

* **md2po** is used to dump strings from Markdown files into pofiles as msgids.
* **po2md** is used to produce a translated Markdown file from a source Markdown
  file and a pofile with extracted msgids and translated msgstrs.
* **mdpo2html** is used to produce a translated HTML file from a source HTML
  file produced from Markdown file using a Markdown-to-HTML converter, and a
  pofile of reference for strings.

.. _md2po-cli:

md2po
=====

.. argparse::
   :module: mdpo.md2po.__main__
   :func: build_parser
   :prog: md2po
   :nodefault:

.. raw:: html

   <hr>

.. _po2md-cli:

po2md
=====

.. argparse::
   :module: mdpo.po2md.__main__
   :func: build_parser
   :prog: po2md
   :nodefault:


.. raw:: html

   <hr>

.. _mdpo2html-cli:

mdpo2html
=========

.. argparse::
   :module: mdpo.mdpo2html.__main__
   :func: build_parser
   :prog: mdpo2html
   :nodefault:
