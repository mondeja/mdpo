************
Contributing
************

Development install
===================

You need to install Poetry >= 1.2.0.

.. code-block:: bash

   git clone https://github.com/mondeja/mdpo.git
   cd mdpo
   poetry install
   pre-commit install
   pip install poetry-exec-plugin


Build documentation
===================

.. code-block:: bash

   poetry exec doc

Test
====

.. code-block:: bash

   poetry exec test

Lint
====

.. code-block:: bash

   poetry exec lint

Release
=======

.. code-block:: bash

   python3 -m bump2version <major/minor/patch>
   git add .
   git commit -m "Bump version"
   git push origin master
   git tag -a v<version>
   git push origin v<version>
