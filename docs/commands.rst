**************************
Customizing the extraction
**************************

You can customize the string extraction process using HTML comments in
your Markdown files.

Disabling extraction
====================

You can disable and enable the extraction of certain strings using
next HTML commments:

* ``<!-- mdpo-disable-next-line -->``
* ``<!-- mdpo-disable -->``
* ``<!-- mdpo-enable -->``
* ``<!-- mdpo-enable-next-line -->``

For example:

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

For example:

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

For example:

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


Extracting comments itself
==========================

You can extract comments inside the pofile, but don't ask me why you need this:

* ``<!-- mdpo-include Message that you want to include -->``

For example:

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
