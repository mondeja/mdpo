************
Contributing
************

Development install
===================

You need to install Poetry >= 1.2.0.

.. code-block:: sh

   git clone https://github.com/mondeja/mdpo
   cd mdpo
   poetry install
   pre-commit install
   poetry self add poetry-exec-plugin

Test
====

.. code-block:: sh

   poetry exec test
   # `poetry exec t`
   # `poetry exec test:show`


Lint
====

.. code-block:: sh

   poetry exec lint


Build documentation
===================

.. code-block:: sh

   poetry exec doc
   # `poetry exec doc:show`

Release
=======

.. code-block:: sh

   version="$(poetry run bump <major/minor/patch>)"
   git add .
   git commit -m "Bump version"
   git push origin master
   git tag -a "v$version"
   git push origin "v$version"
