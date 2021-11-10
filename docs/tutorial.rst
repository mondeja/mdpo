********
Tutorial
********

**mdpo** provides flexible ways for doing Markdown markup translations. In this
tutorial are covered the most common workflows.

.. raw:: html

   <hr>

Markdown to markdown
====================

If you want to translate a Markdown source using PO files and produce
translated Markdown output, use this method.

Given next directory tree:

.. code-block:: bash

   .
   ├── locale
   │   └── es
   │       └── LC_MESSAGES
   └── README.md


Use the next command to create or update the PO file for ``README.md``:

.. code-block:: bash

   md2po README.md --quiet --save --po-filepath locale/es/LC_MESSAGES/readme.po


Then, in order of translate the ``README.md`` producing other file as result:

.. code-block:: bash

   po2md README.md --pofiles locale/es/LC_MESSAGES/readme.po --quiet \
     --save locale/es/LC_MESSAGES/README.md

This will be the output after previous two commands:

.. code-block::

   .
   ├── locale
   │   └── es
   │       └── LC_MESSAGES
   │           ├── README.md
   │           └── readme.po
   └── README.md

.. seealso::
   * :ref:`md2po CLI<md2po-cli>`
   * :ref:`po2md CLI<po2md-cli>`

.. raw:: html

   <hr>

Simple README file translation
==============================

Just use :ref:`md2po2md CLI<md2po2md-cli>`:

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

This will be the output after the previous command:

.. code-block:: bash

   .
   ├── locale
   │   ├── es
   │   |   ├── README.md
   │   |   └── readme.po 
   |   └── fr
   │       ├── README.md
   │       └── readme.po 
   └── README.md

.. seealso::
   * :ref:`md2po2md CLI<md2po2md-cli>`

.. raw:: html

   <hr>

HTML-from-Markdown to HTML
==========================

If you have a HTML file produced from Markdown using a Markdown processor like
`Python-Markdown <markdown_py>`_ and you want to translate it in place using
PO files, use this method.

.. warning::
   This method is experimental. If you have issues consider to open an issue
   in the `bug tracker <bug_tracker>`_.


Given next directory tree:

.. code-block:: bash

   .
   ├── locale
   │   └── es
   │       └── LC_MESSAGES
   ├── README.html
   └── README.md

Where the file ``README.html`` have been produced using an HTML processor, use
next command to create and update the translation pofile for ``README.html``:

.. code-block:: bash

   md2po README.md --quiet --save --po-filepath locale/es/LC_MESSAGES/readme.po

After that, you can use the new file ``locale/es/LC_MESSAGES/readme.po`` to
replace the contents of the file ``README.html`` with your translations, using
next command:

.. code-block:: bash

   mdpo2html README.html --pofiles locale/es/LC_MESSAGES/readme.po --quiet \
     --save locale/es/LC_MESSAGES/README.html

And this will produce your translated file in
``locale/es/LC_MESSAGES/README.html``:

.. code-block::

   .
   ├── locale
   │   └── es
   │       └── LC_MESSAGES
   │           ├── README.html
   │           └── readme.po
   ├── README.html
   └── README.md

.. seealso::
   * :ref:`mdpo2html CLI<mdpo2html-cli>`

.. markdown_py: https://github.com/Python-Markdown/markdown
.. bug_tracker: https://github.com/mondeja/mdpo/issues
