import pytest

from mdpo.md2po import markdown_to_pofile


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-include-codeblock', {}),
        ('on-codeblock', {'on-codeblock': 'include-codeblock'}),
    ),
)
def test_include_indented_codeblock(command, command_aliases):
    content = f'''
<!-- {command} -->

    var hello = "world";
    var hola = "mundo";

This must be included also.

    var thisCodeMustNotBeIncluded = undefined;
'''
    pofile = markdown_to_pofile(content, command_aliases=command_aliases)
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
