**********************
Customizing extraction
**********************

You can customize the string extraction process using HTML comments in
your Markdown files.

.. tip::

   If you want to specify next commands with other names, take a look at the
   argument :ref:`md2po---command-alias` of :ref:`md2po CLI<cli:md2po>` or the
   optional parameter ``command_aliases`` of the :doc:`programmatic APIs<api>`.

Disabling extraction
====================

You can disable and enable the extraction of certain strings using
the next HTML commments:

* ``<!-- mdpo-disable-next-block -->`` or ``<!-- mdpo-disable-next-line -->``: Do not extract the next Markdown block.
* ``<!-- mdpo-disable -->``: Do not extract the content after it.
* ``<!-- mdpo-enable -->``: Extract the content after it.
* ``<!-- mdpo-enable-next-block -->`` or ``<!-- mdpo-enable-next-line -->`` Extract the next Markdown block.

.. rubric:: Example:

.. code-block:: python

   >>> from mdpo.md2po import markdown_to_pofile

   >>> md_content = '''# Header
   ...
   ... This will be included
   ...
   ... <!-- mdpo-disable-next-line -->
   ... This will be ignored.
   ...
   ... This will be included also.
   ...
   ... <!-- mdpo-disable -->
   ... This paragraph compounded by multiples
   ... lines will be ignored.
   ...
   ... # md2po remains disabled for this header
   ...
   ... <!-- mdpo-enable-next-line -->
   ... This line will be included because we have enabled it individually.
   ...
   ... <!-- mdpo-enable -->
   ... All content from here will be extracted...
   ... '''
   >>>
   >>> pofile = markdown_to_pofile(md_content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   msgid "This will be included."
   msgstr ""

   msgid "This will be included also."
   msgstr ""

   msgid "This line will be included because we have enabled it individually."
   msgstr ""

   msgid "All content from here will be extracted..."
   msgstr ""


Including comments for translators
==================================

You can include comments for translators using the next line in the
line before the message:

* ``<!-- mdpo-translator Comment that you want to include -->``

.. rubric:: Example:

.. code-block:: python

   >>> content = '''<!-- mdpo-translator This is a comment for a translator -->
   ... Some text that needs to be clarified
   ...
   ... Some text without comment
   ... '''

   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   #. This is a comment for a translator
   msgid "Some text that needs to be clarified"
   msgstr ""

   msgid "Some text without comment"
   msgstr ""

Contextual markers
==================

You can specify contexts for msgids using next command:

* ``<!-- mdpo-context Context for your string -->``

.. rubric:: Example:

.. code-block:: python

   >>> content = '''<!-- mdpo-context month -->
   ... May
   ...
   ... <!-- mdpo-context might -->
   ... May
   ... '''
   >>>
   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   msgctxt "month"
   msgid "May"
   msgstr ""

   msgctxt "might"
   msgid "May"
   msgstr ""

.. _include-codeblock-command:

Code blocks extraction
======================

You can enable and disable code blocks extraction inside the PO file using
the next commands:

* ``<!-- mdpo-include-codeblocks -->``: Include all codeblocks placed after
  this command (same behaviour as passing the argument
  :ref:`md2po---include-codeblocks` or ``include_codeblocks=True`` if you are
  using the
  :doc:`programmatic interface </dev/reference/mdpo.po2md>`).
* ``<!-- mdpo-disable-codeblocks -->``: Does not include codeblocks placed
  after this command.
* ``<!-- mdpo-include-codeblock -->``: Include next codeblock placed after this
  command.
* ``<!-- mdpo-disable-codeblock -->``: Does not include next codeblock placed
  after this command.

.. rubric:: Indented code block example:

.. code-block:: python

   >>> content = '''
   ... <!-- mdpo-include-codeblock -->
   ...
   ...     var hello = "world";
   ...     var hola = "mundo";
   ...
   ... Another paragraph.
   ... '''
   >>>
   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   msgid ""
   msgstr ""

   msgid ""
   "var hello = \"world\";\n"
   "var hola = \"mundo\";\n"
   msgstr ""

   msgid "Another paragraph."
   msgstr ""

.. rubric:: Fenced code block example:

.. code-block:: python

   >>> content = '''
   ... <!-- mdpo-include-codeblock -->
   ... ```javascript
   ... var hello = "world";
   ... var hola = "mundo";
   ... ```
   ... '''
   >>>
   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   msgid ""
   msgstr ""

   msgid ""
   "var hello = \"world\";\n"
   "var hola = \"mundo\";\n"
   msgstr ""

Extracting comments itself
==========================

You can extract comments inside the PO file, but don't ask me why you need
this:

* ``<!-- mdpo-include Message that you want to include -->``

.. rubric:: Example:

.. code-block:: python

   >>> content = '''<!-- mdpo-include This message will be included -->
   ... Some text
   ... '''

   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   msgid "This message will be included"
   msgstr ""

   msgid "Some text"
   msgstr ""

This command can be used along with ``mdpo-translator``:

.. code-block:: python

   >>> content = '''<!-- mdpo-translator Comment for translator in comment -->
   ... <!-- mdpo-include This comment must be included -->
   ... Some text that needs to be clarified
   ... '''

   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   #. Comment for translator in comment
   msgid "This comment must be included"
   msgstr ""

And with ``mdpo-context``, combining both:

.. code-block:: python

   >>> content = '''<!-- mdpo-context Some context for the included -->
   ... <!-- mdpo-translator Comment for translator in comment -->
   ... <!-- mdpo-include This comment must be included -->
   ... Some text that needs to be clarified
   ... '''

   >>> pofile = markdown_to_pofile(content)
   >>> print(pofile)
   #
   msgid ""
   msgstr ""

   #. Comment for translator in comment
   msgctxt "Some context for the included"
   msgid "This comment must be included"
   msgstr ""
