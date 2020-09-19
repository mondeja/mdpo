*********
Rationale
*********

.. warning::

   This is translating Markdown, **the hard way**.

Why?
====

Using this library implies a complicated way for the programmer to prepare a
translation workflow compared to other solutions. It is designed to make life
easier for the translator and to unificate the translation process of Markdown
files versus other source code files, using ``.po`` files for all, among other
advantages.

Before start using this library, check if you can use the following
approach to solve the problem of translating Markdown.

The traditional approach
========================

Use one Markdown file for each language. This is the most commonly used.
For example, Jekyll plugins like `jekyll-multiple-languages-plugin`_ uses it.

This is a very poor approach because their advantages are less than the
disadvantages, but it's state of the art at the moment of ``mdpo``
specification was conceived:

Advantages
----------

* **Contextualization**: The translator sees the entire file in the translation
  process, which provides a better understanding of what is translating.
* **Programming vagueness**: The programmer don't need to deal with complicated
  translations workflows. He/she can sort files by translation directories or
  whatever. The use of plain files limits the responsibility of the programmer.
* **L18n customization**: The translation can be customized for each language.
  This could be interesting if we have to translate articles for different
  market niches in different countries, but this can be achieved using another
  approach in which those articles were unique for the countries that required
  it, but this is a localization (l18n) problem rather than
  internationalization (i18n).

Disadvantages
-------------

* **Markup errors**: Translators have to learn Markdown language before start
  working in the translations because they need to work with Markdown markup
  directly. The problem of dealing with Markdown markup can be prevented using
  editors that support the syntax, but these editors are not the ones used by
  translators and you, as a programmer can't impose the use of certain tools
  to people that even don't speak your language. You better think that they are
  creating the translations in a notepad using Windows 95. This frequently
  causes failures in markup characters which breaks styles, so in the long run
  they must be revised anyway (sometimes in strange languages) or markup errors
  go unnoticed for a long time.
* **Desynchronization**: A change in one file (the source language frequently)
  requires a manual review of all other files (translations). This is a
  tremendous effort for the translators and therefore an incredible expenditure
  of money for companies. Think about it, the translators have to manually
  review each Markdown file, a format they don't have to be used to, looking
  for these parts that have been updated... It just doesn't make sense.
* **Redundancy**: There are parts of Markdown files that don't need to be
  translated like code blocks. You can tell to the translators that they must
  not translate the content blocks of text wich starts and ends with triple
  backticks (``\```), but at the end of the day, you will have blocks of code
  translated. These blocks, as well as other parts of the source file, must be
  hidden to the translator.

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

Beyound that statement, an artificial intelligence capable of solve the
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

This implies a ``.po`` files translator capable of work with markup character
templates using an editor which allows to create markups like editors do. But,
this thing doesn't exists currently.

mdpo approach
=============

The solution proposed by this library is to extract from Markdown files only
the text that needs to be translated, including markdown characters but
simplifying them:

* ``**Bold text**`` is not changed, is dumped into msgids as ``**Bold text**``.
* ``*Italic text*`` is not changed, is dumped into msgids as ``*Italic text*``.
* ````Code text```` and ```Code text``` are unified to use one backtick
  for start and end characters and dumped into msgids as ```Code text```.
* ``[Link text](target)`` are dumped into msgids removing the target and
  changing markup characters a bit, as ```[Link text]```. The same behaviour
  occurs for ``[referenced links][reference]`` and ``[wiki links]``.
* From images like ``![Image alternative text](/target.ext "Image title text")``,
  title text and alternative text are dumped into msgids, for this case
  ``Image alternative text`` and ``Image title text``.
* ``~~Strikethrough text~~`` is not changed, is dumped into msgids as
  ``~~Strikethrough text~~``.
* ``$LaTeX maths$`` and ``$$LaTeX maths displays$$`` are not changed, are dumped
  into msgids as ``$LaTeX maths$`` and ``$$LaTeX maths displays$$``.
* ``__Underline text__`` and ``_Underline text_`` are unified to
  ``__Underline text__`` into msgids if ``underline`` mode is active,
  otherwise are treated like bold text (with two characters ``__``) and dumped
  as ``**Underline text**`` or italic text (with one character ``_``) and
  dumped as ``*Underline text*``.


Advantages
----------

* Updates into source files are synchronized. A change in one string declares
  the old one fuzzy and the translation can be updated quickly.
* Translators work with ``.po`` files directly, a standard in translations.
* Parts of the Markdown files that do not need translated as code blocks or
  link targets are not included in the translation, reducing possibility of
  markup failures in translations.
* Markup characters are reduced to their minimum expression inside msgids,
  reducing possibility of markup failures in translations.

Disadvantages
-------------

* Msgids markup characters uses a new syntax that is not fully Markdown. This
  is intentionally made for create translation editors that can work with
  markup using template rules, simplifying them to be able to specify characters
  at start and end for each markup type.
* Message replacers needs to be written and depends on this specification.
* Translation editors needs to be configured with this specification if they
  want to handle properly markup character templates.

.. _jekyll-multiple-languages-plugin: https://github.com/kurtsson/jekyll-multiple-languages-plugin
