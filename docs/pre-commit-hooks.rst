****************
pre-commit hooks
****************

For all hooks, there are two different ways to set input paths, using first
positional arguments inside ``args`` property or the ``files`` property as a
regex.

md2po
=====

The ``--save`` and ``--quiet`` options are passed automatically to ``md2po``,
so you don't need to specify them.

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: md2po
         args:
           - README.md
           - -po
           - README.es.po

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: pc-hooks
     hooks:
       - id: md2po
         files: ^README\.md
         args:
           - -po
           - README.es.po

.. seealso::
   * :ref:`md2po CLI<cli:md2po>`

po2md
=====

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: po2md
         args:
           - README.md
           - -po
           - README.es.po
           - -s
           - README.es.md

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: po2md
         files: ^README\.md
         args:
           - -po
           - README.es.po
           - -s
           - README.es.md

.. seealso::
   * :ref:`po2md CLI<cli:po2md>`

md2po2md
========

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: md2po2md
         args:
           - README.md
           - -l
           - es
           - -o
           - locale/{lang}

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: md2po2md
         files: ^README\.md
         args:
           - -l
           - es
           - -l
           - fr
           - -o
           - locale/{lang}

.. seealso::
   * :ref:`md2po2md CLI<cli:md2po2md>`

mdpo2html
=========

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: mdpo2html
         args:
           - README.html
           - -p
           - README.po
           - -s
           - README.es.html

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.74
     hooks:
       - id: mdpo2html
         files: ^README\.html
         args:
           - -p
           - README.po
           - -s
           - README.es.html

.. seealso::
   * :ref:`mdpo2html CLI<cli:mdpo2html>`
