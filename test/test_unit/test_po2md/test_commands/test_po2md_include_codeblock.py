"""It's not needed to include <!-- mdpo-include-codeblock --> command in
Markdown files, only if code block contents are included in PO files will be
translated directly.
"""

from mdpo.po2md import pofile_to_markdown


def test_include_indented_codeblock(tmp_file):
    markdown_input = '''
    var hello = "world";
    var this;

This must be translated.

    var thisCodeMustNotBeEdited = undefined;
'''

    markdown_output = '''    var hola = "mundo";
    var esto;

Esto debe ser traducido.

    var thisCodeMustNotBeEdited = undefined;
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var this;\\n"
msgstr ""
"var hola = \\"mundo\\";\\n"
"var esto;\\n"

msgid "This must be translated."
msgstr "Esto debe ser traducido."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output


def test_include_fenced_codeblock(tmp_file):
    markdown_input = '''```javascript
var hello = "world";
var this;
```

This must be translated.

```javascript
var thisCodeMustNotBeEdited = undefined;
```
'''

    markdown_output = '''```javascript
var hola = "mundo";
var esto;
```

Esto debe ser traducido.

```javascript
var thisCodeMustNotBeEdited = undefined;
```
'''

    pofile_content = '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var this;\\n"
msgstr ""
"var hola = \\"mundo\\";\\n"
"var esto;\\n"

msgid "This must be translated."
msgstr "Esto debe ser traducido."
'''

    with tmp_file(pofile_content, '.po') as po_filepath:
        output = pofile_to_markdown(markdown_input, po_filepath)
    assert output == markdown_output
