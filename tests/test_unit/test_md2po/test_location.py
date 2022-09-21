import os

from mdpo.md2po import markdown_to_pofile


def test_location_paragraphs(tmp_file, wrap_location_comment):
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

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (paragraph)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (header)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (unordered list)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (unordered list)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (ordered list)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (ordered list)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (quote)')}
msgid "Foo 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (quote)')}
msgid "Foo 8"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (quote)')}
msgid "Foo 9"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)
    assert str(output) == expected_output


def test_location_headers(tmp_file, wrap_location_comment):
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

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (header)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (ordered list)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (ordered list)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (quote)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (quote)')}
msgid "Foo 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (quote)')}
msgid "Foo 8"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)
    assert str(output) == expected_output


def test_location_quotes(tmp_file, wrap_location_comment):
    markdown_content = '''> Foo 1

- Foo 2
- Foo 3
   > Foo 4

1. # Foo 5

> > Foo 6
>
> > Foo 7
'''

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (quote)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 4 (ordered list)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (quote)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (quote)')}
msgid "Foo 7"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)

    assert str(output) == expected_output


def test_location_unordered_lists(tmp_file, wrap_location_comment):
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

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (unordered list)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (ordered list)')}
msgid "Foo 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (ordered list)')}
msgid "Foo 8"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (ordered list)')}
msgid "Foo 9"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (ordered list)')}
msgid "Foo 10"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 11"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 12"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 13"
msgstr ""
'''
        output = markdown_to_pofile(md_filepath)

    assert str(output) == expected_output


def test_location_ordered_lists(tmp_file, wrap_location_comment):
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

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (ordered list)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 8"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 9"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (unordered list)')}
msgid "Foo 10"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 11"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 12"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Foo 13"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)
    assert str(output) == expected_output


def test_location_code_blocks(tmp_file, wrap_location_comment):
    markdown_content = '''<!-- mdpo-include-codeblock -->
```python
foo = "bar"
```

```javascript
var foo = "bar";
```

<!-- mdpo-include-codeblock -->

    int foo;

- Foo
   - Bar

      <!-- mdpo-include-codeblock -->
      ```python
      code_which_must_be_included = True
      ```

> <!-- mdpo-include-codeblock -->
> ```javascript
> var codeWhichMustBeIncluded = true;
> ```
'''

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (code)')}
msgid "foo = \\"bar\\"\\n"
msgstr ""

{wrap_location_comment(md_filepath, 'block 5 (code)')}
msgid "int foo;\\n"
msgstr ""

{wrap_location_comment(md_filepath, 'block 6 (unordered list)')}
msgid "Foo"
msgstr ""

{wrap_location_comment(md_filepath, 'block 6 (unordered list)')}
msgid "Bar"
msgstr ""

{wrap_location_comment(md_filepath, 'block 6 (unordered list)')}
msgid "code_which_must_be_included = True\\n"
msgstr ""

{wrap_location_comment(md_filepath, 'block 7 (quote)')}
msgid "var codeWhichMustBeIncluded = true;\\n"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)
    assert str(output) == expected_output


def test_location_html(tmp_file, wrap_location_comment):
    markdown_content = '''<!-- a comment -->

<!-- another comment -->

paragraph
'''

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (paragraph)')}
msgid "paragraph"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)
    assert str(output) == expected_output


def test_location_tables(tmp_file, wrap_location_comment):
    markdown_content = '''paragraph

| Foo 1      | Foo 2  | Foo 3  | Foo 4  |
| ---------- | :----- | -----: | :----: |
| Foo 5      | Foo 6  | Foo 7  | Foo 8  |
| Foo 9      | Foo 10 | Foo 11 | Foo 12 |

> | Bar 1      | Bar 2  | Bar 3  | Bar 4  |
> | ---------- | :----- | -----: | :----: |
> | Bar 5      | Bar 6  | Bar 7  | Bar 8  |
> | Bar 9      | Bar 10 | Bar 11 | Bar 12 |
'''

    with tmp_file(markdown_content, '.md') as md_filepath:
        expected_output = f'''#
msgid ""
msgstr ""

{wrap_location_comment(md_filepath, 'block 1 (paragraph)')}
msgid "paragraph"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 8"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 9"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 10"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 11"
msgstr ""

{wrap_location_comment(md_filepath, 'block 2 (table)')}
msgid "Foo 12"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 1"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 2"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 3"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 4"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 5"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 6"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 7"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 8"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 9"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 10"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 11"
msgstr ""

{wrap_location_comment(md_filepath, 'block 3 (quote)')}
msgid "Bar 12"
msgstr ""
'''

        output = markdown_to_pofile(md_filepath)

    assert str(output) == expected_output


def test_location_file_independent(tmp_dir):
    """Location block counters should be reset for each file."""
    with tmp_dir([
        ('foo.md', '# Foo\n'),
        ('bar.md', '# Bar\n'),
    ]) as (filesdir, foo_md_filepath, bar_md_filepath):
        expected_output = f'''#
msgid ""
msgstr ""

#: {bar_md_filepath}:block 1 (header)
msgid "Bar"
msgstr ""

#: {foo_md_filepath}:block 1 (header)
msgid "Foo"
msgstr ""
'''

        output = markdown_to_pofile(os.path.join(filesdir, '*.md'))

    assert str(output) == expected_output
