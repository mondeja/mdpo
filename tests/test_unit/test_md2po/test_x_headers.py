from mdpo.md2po import markdown_to_pofile
from mdpo.md4c import DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS


try:
    import importlib_metadata
except ImportError:
    import importlib.metadata as importlib_metadata


def test_xheader_included():
    markdown_content = '# Foo\n'

    extensions = DEFAULT_MD4C_GENERIC_PARSER_EXTENSIONS + ['underline']
    pofile = markdown_to_pofile(
        markdown_content,
        xheader=True,
        plaintext=False,
        extensions=extensions,
    )
    assert str(pofile) == f'''#
msgid ""
msgstr "X-Generator: mdpo v{importlib_metadata.version("mdpo")}\\n"

msgid "Foo"
msgstr ""
'''
