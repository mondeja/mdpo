from mdpo import markdown_to_pofile


def test_location_paragraphs(tmp_file):
    markdown_content = '''Foo 1

# Foo 2

- Foo 3
   - Foo 4

1. Foo 5
   1. Foo 6

> Foo 7
>
> - Foo 8
>
> 1. Foo 9
'''

    with tmp_file('#\nmsgid ""\nmsgstr ""\n', '.po') as po_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

#: {po_filepath}:block 1 (paragraph)
msgid "Foo 1"
msgstr ""

#: {po_filepath}:block 2 (header)
msgid "Foo 2"
msgstr ""

#: {po_filepath}:block 3 (unordered list)
msgid "Foo 3"
msgstr ""

#: {po_filepath}:block 3 (unordered list)
msgid "Foo 4"
msgstr ""

#: {po_filepath}:block 4 (ordered list)
msgid "Foo 5"
msgstr ""

#: {po_filepath}:block 4 (ordered list)
msgid "Foo 6"
msgstr ""

#: {po_filepath}:block 5 (quote)
msgid "Foo 7"
msgstr ""

#: {po_filepath}:block 5 (quote)
msgid "Foo 8"
msgstr ""

#: {po_filepath}:block 5 (quote)
msgid "Foo 9"
msgstr ""
'''

        output = markdown_to_pofile(markdown_content, po_filepath=po_filepath)
    assert str(output) == expected_output


def test_location_headers(tmp_file):
    markdown_content = '''# Foo 1

- # Foo 2
   - # Foo 3

1. # Foo 4
   1. Foo 5

> # Foo 6
>
> - # Foo 7
>
> 1. # Foo 8
'''

    with tmp_file('#\nmsgid ""\nmsgstr ""\n', '.po') as po_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

#: {po_filepath}:block 1 (header)
msgid "Foo 1"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 2"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 3"
msgstr ""

#: {po_filepath}:block 3 (ordered list)
msgid "Foo 4"
msgstr ""

#: {po_filepath}:block 3 (ordered list)
msgid "Foo 5"
msgstr ""

#: {po_filepath}:block 4 (quote)
msgid "Foo 6"
msgstr ""

#: {po_filepath}:block 4 (quote)
msgid "Foo 7"
msgstr ""

#: {po_filepath}:block 4 (quote)
msgid "Foo 8"
msgstr ""
'''

        output = markdown_to_pofile(markdown_content, po_filepath=po_filepath)
    assert str(output) == expected_output


def test_location_quotes(tmp_file):
    markdown_content = '''> Foo 1

- Foo 2
- Foo 3
   > Foo 4

1. # Foo 5

> > Foo 6
>
> > Foo 7
'''

    with tmp_file('#\nmsgid ""\nmsgstr ""\n', '.po') as po_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

#: {po_filepath}:block 1 (quote)
msgid "Foo 1"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 2"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 3"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 4"
msgstr ""

#: {po_filepath}:block 4 (ordered list)
msgid "Foo 5"
msgstr ""

#: {po_filepath}:block 5 (quote)
msgid "Foo 6"
msgstr ""

#: {po_filepath}:block 5 (quote)
msgid "Foo 7"
msgstr ""
'''

        output = markdown_to_pofile(markdown_content, po_filepath=po_filepath)

    assert str(output) == expected_output


def test_location_unordered_lists(tmp_file):
    markdown_content = '''- Foo 1
- Foo 2
   - Foo 3
      - Foo 4
   - Foo 5
- Foo 6

1. Foo 7
1. Foo 8
   - Foo 9
   - Foo 10

> Foo 11
>
> - Foo 12
>    - Foo 13
'''

    with tmp_file('#\nmsgid ""\nmsgstr ""\n', '.po') as po_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 1"
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 2"
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 3"
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 4"
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 5"
msgstr ""

#: {po_filepath}:block 1 (unordered list)
msgid "Foo 6"
msgstr ""

#: {po_filepath}:block 2 (ordered list)
msgid "Foo 7"
msgstr ""

#: {po_filepath}:block 2 (ordered list)
msgid "Foo 8"
msgstr ""

#: {po_filepath}:block 2 (ordered list)
msgid "Foo 9"
msgstr ""

#: {po_filepath}:block 2 (ordered list)
msgid "Foo 10"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 11"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 12"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 13"
msgstr ""
'''
        output = markdown_to_pofile(markdown_content, po_filepath=po_filepath)

    assert str(output) == expected_output


def test_location_ordered_lists(tmp_file):
    markdown_content = '''1. Foo 1
1. Foo 2
   1. Foo 3
      1. Foo 4
   1. Foo 5
1. Foo 6

- Foo 7
- Foo 8
   1. Foo 9
   1. Foo 10

> Foo 11
>
> 1. Foo 12
>    1. Foo 13
'''

    with tmp_file('#\nmsgid ""\nmsgstr ""\n', '.po') as po_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 1"
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 2"
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 3"
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 4"
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 5"
msgstr ""

#: {po_filepath}:block 1 (ordered list)
msgid "Foo 6"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 7"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 8"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 9"
msgstr ""

#: {po_filepath}:block 2 (unordered list)
msgid "Foo 10"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 11"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 12"
msgstr ""

#: {po_filepath}:block 3 (quote)
msgid "Foo 13"
msgstr ""
'''

        output = markdown_to_pofile(markdown_content, po_filepath=po_filepath)
    assert str(output) == expected_output
