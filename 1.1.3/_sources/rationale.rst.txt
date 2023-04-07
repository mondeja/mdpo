****************
mdpo's rationale
****************

Are markup characters part of a translation?
============================================

Infinite state machine approach
-------------------------------

A long time ago I read on StackOverflow that a good translation process is one
that does not include markup characters inside source and target languages.
I partially agree with that statement, but it implies the existence of an ideal
world in what we can remove all markup characters of source file, send to our
translators a plain text file, and when the translation is returned to us, we
could rebuilt the markup characters in the target language. As long as there
is no artificial intelligence capable of doing that in a stable way, we need
to look for other ways to fix the problem.

Beyond that statement, an artificial intelligence capable of solve the
problem or rebuild the target language file would be possible? I don't know,
but think about next simple example. This machine would need to be able to
translate the Markdown string ``**Flexible** replacement **again**`` to the
Spanish ``Reemplazamiento **flexible de nuevo**``, giving it as input the
strings ``Reemplazamiento flexible de nuevo`` and
``**Flexible** replacement **again**``. For this simple example maybe it could
learn it without big problems, but think about idiomatic twists, language
contexts and the growth of languages in an ever-changing world within the
framework of a stable translation process at the cost of expensive learning
procedures.

Do you want to wait for a machine capable of doing such a large job to appear
to have acceptable translations? Personally I don't.

Do the markup characters express meaning?
-----------------------------------------

In one language could be a sentence with bold characters in a part of a
sentence that could express meaning. This meaning could be expressed in another
way in other language. So I declare that a good translation process is one that
allows markup characters without the need to force the translator to do mental
juggling working with them.

This implies a PO files translator capable of work with markup characters
templates using an editor which allows to create markups like editors do. But,
this thing doesn't exists currently.

mdpo approach
=============

The solution proposed by this library is to extract from Markdown files only
the text that needs to be translated, including markdown characters:

* ``**Bold text**`` is not changed, is dumped into msgids as ``**Bold text**``.
* ``*Italic text*`` is not changed, is dumped into msgids as ``*Italic text*``.
* ````Code text```` and ```Code text``` are unified to use the minimum possible
  backticks for start and end characters and dumped into msgids as
  ```Code text```.
* ``[Link text](target)`` is not changed if the text is different than the
  target, is dumped into msgids as is. In the case that link text and target
  are equal, is converted to an `autolink`_ and dumped into msgids as
  ``<link>``.
* Images as ``![Image alternative text](/target.ext "Image title text")``,
  are not changed, but included as is.
* ``~~Strikethrough text~~`` is not changed, is dumped into msgids as
  ``~~Strikethrough text~~``.
* ``$LaTeX maths$`` and ``$$LaTeX maths displays$$`` are not changed, are dumped
  into msgids as ``$LaTeX maths$`` and ``$$LaTeX maths displays$$``.
* ``__Underline text__`` and ``_Underline text_`` are unified to
  ``__Underline text__`` into msgids if ``underline`` mode is active,
  otherwise are treated like bold text (with two characters ``__``) and dumped
  as ``**Underline text**`` or italic text (with one character, ``_``) and
  dumped as ``*Underline text*``.

.. tip::

   Using the option :ref:`md2po---xheader` of :ref:`md2po CLI <cli:md2po>` you can sign this
   specification in the affected files.

.. seealso::
   * :ref:`Implementation notes<implementation-notes>`

Advantages
----------

* Updates into source files are synchronized. A change in one string declares
  the old one obsolete and the translation can be updated quickly.
* Translators work with PO files directly, an open source standard for
  translations.
* Parts of the Markdown files that do not need to be translated as code blocks
  or are not included in the translation (by default), reducing possibility of
  markup failures in translations.

.. _autolink: https://spec.commonmark.org/0.30/#autolinks
