Install
=======

You must install Pandoc<=2.9 first:

.. code-block:: bash

   pip install pypandoc
   python -c "import pypandoc as p;p.download_pandoc(version='2.9', delete_installer=True);"


...and then:

.. code-block:: bash

   pip install md2po
