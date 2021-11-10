***********************
Command line interfaces
***********************

mdpo installation includes four command line interfaces:

* **md2po** is used to dump strings from Markdown files into PO files as msgids.
* **po2md** is used to produce a translated Markdown file from a source Markdown
  file and a PO file with extracted msgids and translated msgstrs.
* **md2po2md** is a convenient wrapper for **md2po** and **po2md**.
* **mdpo2html** is used to produce a translated HTML file from a source HTML
  file produced from Markdown file using a Markdown-to-HTML converter, and a
  PO file of reference for strings.

.. raw:: html

   <hr>

md2po
=====

.. sphinx_argparse_cli::
   :module: mdpo.md2po.__main__
   :func: build_parser
   :prog: md2po
   :title:

.. raw:: html

   <hr>

po2md
=====

.. sphinx_argparse_cli::
   :module: mdpo.po2md.__main__
   :func: build_parser
   :prog: po2md
   :title:

markdownlint compatible configuration
*************************************

The output produced by :ref:`cli:po2md` is compatible with the
 following `Markdownlint configuration`_:

.. code-block:: json

   {
     "no-blanks-blockquote": false,
     "no-bare-urls": false,
     "ul-indent": {
       "indent": 3
     }
   }

.. raw:: html

   <hr>

md2po2md
========

.. sphinx_argparse_cli::
   :module: mdpo.md2po2md.__main__
   :func: build_parser
   :prog: md2po2md
   :title:

.. raw:: html

   <hr>

mdpo2html
=========

.. sphinx_argparse_cli::
   :module: mdpo.mdpo2html.__main__
   :func: build_parser
   :prog: mdpo2html
   :title:

.. raw:: html

   <script>
   var argumentsSubsectionTitles = document.getElementsByTagName("H3");
   for (let i=0; i<argumentsSubsectionTitles.length; i++) {
     let subsectionTitle = argumentsSubsectionTitles[i].childNodes[0];
     if (subsectionTitle.data.indexOf("markdownlint") == -1) {
       subsectionTitle.data = subsectionTitle.data.split(" ").slice(1).join(" ");
     }
   }
   </script>

.. _Markdownlint configuration: https://github.com/DavidAnson/markdownlint#configuration
