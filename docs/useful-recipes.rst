**************
Useful recipes
**************

Simple README file translation
==============================

This is the simplest way that I've found to translate the READMEs of my
projects. Just use :ref:`md2po2md CLI<md2po2md-cli>`:

.. code-block:: bash

   md2po2md README.md -l es -l fr -o "locale/{lang}"

Define the languages to translate into using the ``-l`` option.

You also can use the next snippet to include links for the translations:

.. code-block:: html

   <!-- mdpo-disable -->
   <!-- mdpo-enable-next-line -->
   > Read this document in other languages:
   >
   > - [Español][readme-es]
   > - [Français][readme-fr]
   <!-- mdpo-enable -->

   [readme-es]: https://github.com/user/repo/blob/master/locale/es/README.md
   [readme-fr]: https://github.com/user/repo/blob/master/locale/fr/README.md
