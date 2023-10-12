import os

from mdpo.po2md import pofile_to_markdown


def test_multiple_pofiles_glob(tmp_dir):
    markdown_content = '''
Beyond good intentions, a dictatorship is a dictatorship.

How is it that you think beautiful nerd?
'''

    expected_output = (
        '''Más allá de las buenas intenciones, una dictadura es una dictadura.

¿Cómo es que te parece nerd lo bello?
''')

    with tmp_dir({
        'foo.po': '''#
msgid ""
msgstr ""

msgid "Beyond good intentions, a dictatorship is a dictatorship."
msgstr "Más allá de las buenas intenciones, una dictadura es una dictadura."
''',
        'bar.po': '''#
msgid ""
msgstr ""

msgid "How is it that you think beautiful nerd?"
msgstr "¿Cómo es que te parece nerd lo bello?"
''',
    }) as filesdir:
        assert pofile_to_markdown(
            markdown_content,
            os.path.join(filesdir, '*.po'),
        ) == expected_output
