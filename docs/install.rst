*******
Install
*******

Linux
=====

.. code-block:: bash

   pip install \
     -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c \
     && pip install mdpo

Specifying in requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   -e git+https://github.com/dominickpastore/pymd4c.git@master#egg=md4c
   mdpo


MacOS and Windows users
=======================

This library depends on `pymd4c`_, which is not installed automatically in
Windows and MacOS distributions, so you need to install it
`building from source`_.


.. _pymd4c: https://github.com/dominickpastore/pymd4c
.. _building from source: https://github.com/dominickpastore/pymd4c#build-and-install-from-source
