.. _implementation-notes:

********************
Implementation notes
********************

.. note::

   Refer to the `CommonMark Specification v0.30`_ for descriptions of the terms
   used by this document.

Autolink vs link clash
======================

An autolink is something like ``<https://foo.bar>`` and a link is something
like ``[foo](https://foo.bar)``.

MD4C parser doesn't distinguish between an autolink and a link whose text and
destination is the same. So, mdpo will treat all links whose text and
destination is the same as autolinks.

If a link has inside his text markup characters, even if its content if the
same as its target, will be treated as different and rendered as a link. So,
in practice: if a link text has markup characters, can't be an autolink.

Link cloisterers
================

* Collapsed reference links like ``[foo][]`` and links with same text and href
  like ``[foo][foo]`` are both normalized to ``[foo]`` due to MD4C parser
  limitations.
* Although a link title can be wrapped between different characters, mdpo will
  use double quotes characters ``"`` always.

.. _CommonMark Specification v0.30: https://spec.commonmark.org/0.30
