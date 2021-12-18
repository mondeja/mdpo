************
Contributing
************

Development install
===================

.. code-block:: bash

   git clone https://github.com/mondeja/mdpo.git
   python3 -m ensurepip
   python3 -m pip install virtualenv
   python3 -m virtualenv venv
   . venv/bin/activate
   python3 -m pip install -e .[dev]
   pre-commit install


Build documentation
===================

.. code-block:: bash

   python3 setup.py build_sphinx

Test
====

.. code-block:: bash

   python3 -m pytest -s

Lint
====

.. code-block:: bash

   pre-commit run --all-files

Release
=======

.. code-block:: bash

   python3 -m bump2version <major/minor/patch>
   git add .
   git commit -m "Bump version"
   git push origin master
   git tag -a v<version>
   git push origin v<version>
