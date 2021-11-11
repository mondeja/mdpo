****************
Public mdpo APIs
****************

On versions next to Python3.6 you can import public functions from
:doc:`mdpo<devref/index>` package:

.. code-block:: python

   from mdpo import markdown_to_pofile

On Python3.6 you need to import them from the package of each implementation:

.. code-block:: python

   from mdpo.md2po import markdown_to_pofile

md2po
=====

.. automodule:: mdpo.md2po
   :members: markdown_to_pofile

po2md
=====

.. automodule:: mdpo.po2md
   :members: pofile_to_markdown

md2po2md
========

.. automodule:: mdpo.md2po2md
  :members: markdown_to_pofile_to_markdown

mdpo2html
=========

.. automodule:: mdpo.mdpo2html
   :members: markdown_pofile_to_html
