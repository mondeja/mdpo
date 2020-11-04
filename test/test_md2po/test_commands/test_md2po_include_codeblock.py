from mdpo.md2po import markdown_to_pofile


def test_include_indented_codeblock():
    content = '''
<!-- mdpo-include-codeblock -->

    var hello = "world";
    var hola = "mundo";

This must be included also.

    var thisCodeMustNotBeIncluded = undefined;
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var hola = \\"mundo\\";\\n"
msgstr ""

msgid "This must be included also."
msgstr ""
'''


def test_include_fenced_codeblock():
    content = '''
<!-- mdpo-include-codeblock -->
```javascript
var hello = "world";
var hola = "mundo";
```

This must be included also.

```javascript
var thisCodeMustNotBeIncluded = undefined;
```
'''
    pofile = markdown_to_pofile(content)
    assert pofile.__unicode__() == '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var hola = \\"mundo\\";\\n"
msgstr ""

msgid "This must be included also."
msgstr ""
'''
