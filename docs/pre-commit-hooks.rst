****************
pre-commit hooks
****************

md2po
=====

The ``--save`` and ``--quiet`` options are passed automatically to ``md2po``,
so you don't need to specify them in the ``args`` hook property.

There is different ways to set input paths, using first positional arguments
inside ``args`` property or setting the ``files`` property as a regex.

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.65
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
         args:
           - -po
           - README.es.po
         files: README\.md

.. seealso::
   * :ref:`md2po CLI<md2po-cli>`

po2md
=====

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.65
     hooks:
       - id: po2md
         args:
           - README.md
           - -po
           - README.es.po
           - -s
           - README.es.md

.. seealso::
   * :ref:`po2md CLI<po2md-cli>`

md2po2md
========

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: v0.3.65
     hooks:
       - id: md2po2md
         args:
           - prueba.md
           - -l
           - es
           - -o
           - locale/{lang}

.. seealso::
   * :ref:`md2po2md CLI<md2po2md-cli>`
