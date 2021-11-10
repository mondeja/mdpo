The traditional approach
========================

One Markdown file for each language. This is the most commonly used approach to
Markdown translations. For example, site generator plugins like
`jekyll-multiple-languages-plugin`_ and `mkdocs-static-i18n-plugin`_ use it.

Advantages
----------

* **Contextualization**: The translator sees the entire file in the translation
  process, which can provide a better understanding of what is translating.
* **Programming vagueness**: The programmer don't need to deal with complicated
  translations workflows. He/she can sort files by translation directories or
  whatever other simple layout. The use of plain files limits the
  responsibility of the programmer.

Disadvantages
-------------

* **Markup errors**: Translators have to learn Markdown language before start
  working in the translations because they need to work with Markdown markup
  directly.

  The problem of dealing with Markdown markup can be prevented using editors
  that support the syntax, but these editors are not the ones translators are
  used to and you, as a programmer can't impose the usage of certain tools to
  people that even don't speak your language. You better think that they are
  creating the translations in a notepad using Windows 95.

  This frequently causes failures in markup characters which breaks styles, so
  in the long run they must be revised anyway (sometimes in strange languages)
  or markup errors go unnoticed for a long time.

* **Desynchronization**: A change in one file (the source language frequently)
  requires a manual review of all other files (translations).

  This is a tremendous effort for the translators and therefore an incredible
  expenditure of money for companies. Think about it, the translators have to
  manually review each Markdown file, a format they don't have to be used to,
  looking for these parts that have been updated... It just doesn't make sense.

* **Redundancy**: There are parts of Markdown files that don't need to be
  translated, like code blocks. You can tell to the translators that they must
  ignore content inside blocks of text wich starts and ends with triple
  backticks (`````), but at the end of the day, you will have blocks of code
  translated. These blocks, as well as other parts of the source file, must be
  hidden to the translator.

.. _jekyll-multiple-languages-plugin: https://github.com/kurtsson/jekyll-multiple-languages-plugin
.. _mkdocs-static-i18n-plugin: https://ultrabug.github.io/mkdocs-static-i18n/en/
