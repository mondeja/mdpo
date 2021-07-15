**************
Useful recipes
**************

Simple README file translation
==============================

I think that this is the simplest way that I've found to translate the READMEs
of my projects. Just create a folder ``locale/`` with language folders inside
and execute the next line (posix shell):

.. code-block:: bash

   langs=( es ); for l in "${langs[@]}"; do md2po -qs README.md -po locale/$l/README.po && po2md -q README.md -s locale/$l/README.md -p locale/$l/README.po; done

Define the languages to translate into using the ``langs`` variable separating
them by spaces.

You also can use the next snippet to include links for the translations:

.. code-block:: html

   <!-- mdpo-disable -->
   <!-- mdpo-enable-next-line -->
   > Read this document in other languages:
   >
   > - [Español][readme-es]
   <!-- mdpo-enable -->

   [readme-es]: https://github.com/user/repo/blob/master/locale/es/README.md
