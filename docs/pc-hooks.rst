****************
pre-commit hooks
****************

md2po
=====

.. code-block:: yaml

   - repo: https://github.com/mondeja/mdpo
     rev: pc-hooks
     hooks:
       - id: md2po
         args:
           - README.md
           - -po
           - README.po

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
