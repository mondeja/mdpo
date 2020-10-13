************
Installation
************

You need to compile `md4c`_ before install, and then:

.. code-block:: bash

   pip install \
     -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c \
     && pip install mdpo

Specifying in requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c
   mdpo

.. _md4c: https://github.com/mity/md4c/wiki/Building-MD4C
.. _pymd4c: https://github.com/dominickpastore/pymd4c
