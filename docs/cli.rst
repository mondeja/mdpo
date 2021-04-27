***********************
Command line interfaces
***********************

mdpo installation includes three command line interfaces:

* **md2po** is used to dump strings from Markdown files into pofiles as msgids.
* **po2md** is used to produce a translated Markdown file from a source Markdown
  file and a pofile with extracted msgids and translated msgstrs.
* **mdpo2html** is used to produce a translated HTML file from a source HTML
  file produced from Markdown file using a Markdown-to-HTML converter, and a
  pofile of reference for strings.

.. raw:: html

   <hr>

.. _md2po-cli:

md2po
=====

.. sphinx_argparse_cli::
   :module: mdpo.md2po.__main__
   :func: build_parser
   :prog: md2po
   :title:

.. raw:: html

   <hr>

.. _po2md-cli:

po2md
=====

.. sphinx_argparse_cli::
   :module: mdpo.po2md.__main__
   :func: build_parser
   :prog: po2md
   :title:

.. raw:: html

   <hr>

.. _mdpo2html-cli:

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
     subsectionTitle.data = subsectionTitle.data.split(" ").slice(1).join(" ");
   }
   </script>
