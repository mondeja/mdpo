**************************
Customizing the extraction
**************************

You can customize the string extraction process using HTML comments in
your Markdown files.

Disabling extraction
====================

You can disable and enable the extraction of certain strings using
next HTML commments:

* ``<!-- md2po-disable-next-line -->``
* ``<!-- md2po-disable -->``
* ``<!-- md2po-enable -->``
* ``<!-- md2po-enable-next-line -->``

For example:

.. code-block:: python

   >>> from md2po import markdown_to_pofile

   >>> md_content = '''# Header
   ...
   ... This will be included
   ...
   ... <!-- md2po-disable-next-line -->
   ... This will be ignored.
   ...
   ... This will be included also.
   ...
   ... <!-- md2po-disable -->
   ... This paragraph compounded by multiples
   ... lines will be ignored.
   ...
   ... # md2po remains disabled for this header
   ...
   ... <!-- md2po-enable-next-line -->
   ... This line will be included because we have enabled it individually.
   ...
   ... <!-- md2po-enable -->
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

* ``<!-- md2po-translator Comment that you want to include -->``

For example:

.. code-block:: python

   >>> content = '''<!-- md2po-translator This is a comment for a translator -->
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

* ``<!-- md2po-context Context for your string -->``

For example:

.. code-block:: python

   >>> content = '''<!-- md2po-context month -->
   ... May
   ...
   ... <!-- md2po-context might -->
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

* ``<!-- md2po-include Message that you want to include -->``

For example:

.. code-block:: python

   >>> content = '''<!-- md2po-include This message will be included -->
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
