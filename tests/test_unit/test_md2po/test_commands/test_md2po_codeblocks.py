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
    assert pofile == '''#
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
    assert pofile == '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var hola = \\"mundo\\";\\n"
msgstr ""

msgid "This must be included also."
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable-codeblock', {}),
        ('off-codeblock', {'off-codeblock': 'disable-codeblock'}),
    ),
)
def test_disable_next_codeblock(command, command_aliases):
    content = f'''
<!-- {command} -->

    var hello = "world";
    var hola = "mundo";

This must be included.

```javascript
var thisCodeMustBeIncluded = undefined;
```
'''
    pofile = markdown_to_pofile(
        content,
        command_aliases=command_aliases,
        include_codeblocks=True,
    )
    assert pofile == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "var thisCodeMustBeIncluded = undefined;\\n"
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-disable-codeblocks', {}),
        ('off-codeblocks', {'off-codeblocks': 'disable-codeblocks'}),
    ),
)
def test_disable_codeblocks(command, command_aliases):
    content = f'''

    var hello = "world";
    var hola = "mundo";

<!-- {command} -->

This must be included.

```javascript
var thisCodeMustBeIncluded = undefined;
```
'''
    pofile = markdown_to_pofile(
        content,
        command_aliases=command_aliases,
        include_codeblocks=True,
    )
    assert pofile == '''#
msgid ""
msgstr ""

msgid ""
"var hello = \\"world\\";\\n"
"var hola = \\"mundo\\";\\n"
msgstr ""

msgid "This must be included."
msgstr ""
'''


@pytest.mark.parametrize(
    ('command', 'command_aliases'), (
        ('mdpo-include-codeblocks', {}),
        ('on-codeblocks', {'on-codeblocks': 'include-codeblocks'}),
    ),
)
def test_include_codeblocks(command, command_aliases):
    content = f'''

    var hello = "world";
    var hola = "mundo";

<!-- {command} -->

This must be included.

```javascript
var thisCodeMustBeIncluded = undefined;
```
'''
    pofile = markdown_to_pofile(
        content,
        command_aliases=command_aliases,
        include_codeblocks=False,
    )
    assert pofile == '''#
msgid ""
msgstr ""

msgid "This must be included."
msgstr ""

msgid "var thisCodeMustBeIncluded = undefined;\\n"
msgstr ""
'''
