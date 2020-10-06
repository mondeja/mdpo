********
Tutorial
********

mdpo provides different methods for Markdown markup translations.

Markdown to markdown
====================

If you want to translate a Markdown source using ``.po`` files and produce
translated Markdown output, use this method.

Given next directory tree:

.. code-block:: bash

   .
   ├── locale
   │   └── es
   │       └── LC_MESSAGES
   └── README.md


Use the next command to create and update the translation pofile for
``README.md``:

.. code-block:: bash

   md2po README.md --quiet --save --po-filepath locale/es/LC_MESSAGES/readme.po


And, in order of translate the ``README.md`` producing other file as result:

.. code-block:: bash

   po2md README.md --pofiles locale/es/LC_MESSAGES/readme.po --quiet \
     --save locale/es/LC_MESSAGES/README.md

This will be the output after that two commands:

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


..

HTML-from-Markdown to HTML
==========================

If you have a HTML file produced from Markdown file using a Markdown processor
like `Python-Markdown <markdown_py>`_ and want to translate it in place using ``.po`` files, use
this method.

.. warning::
   This method is experimental. If you have issues consider open an issue
   in the `bug tracker <https://github.com/mondeja/mdpo/issues>`_


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
to replace the contents of the file ``README.html`` with your translations,
using next command:

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

.. markdown_py: https://github.com/Python-Markdown/markdown
