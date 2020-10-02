import os
import shutil
import tempfile
from uuid import uuid4

from mdpo.po2md import pofile_to_markdown


def test_multiple_pofiles_glob():
    tmpdir = tempfile.gettempdir()

    pofiles_dirpath = os.path.join(tmpdir, uuid4().hex)
    os.mkdir(pofiles_dirpath)

    pofile_a_filename = uuid4().hex + '.po'
    pofile_a_content = '''#
msgid ""
msgstr ""

msgid "Beyond good intentions, a dictatorship is a dictatorship."
msgstr "Más allá de las buenas intenciones, una dictadura es una dictadura."
'''

    pofile_b_filename = uuid4().hex + '.po'
    pofile_b_content = '''#
msgid ""
msgstr ""

msgid "How is it that you think beautiful nerd? Gaaaaaay"
msgstr "¿Cómo es que te parece nerd lo bello? Gaaaaaay"
'''

    with open(os.path.join(pofiles_dirpath, pofile_a_filename), "w") as f:
        f.write(pofile_a_content)
    with open(os.path.join(pofiles_dirpath, pofile_b_filename), "w") as f:
        f.write(pofile_b_content)

    pofiles_glob = os.path.join(pofiles_dirpath, '*.po')

    markdown_content = """
Beyond good intentions, a dictatorship is a dictatorship.

How is it that you think beautiful nerd? Gaaaaaay
"""
    output = pofile_to_markdown(markdown_content, pofiles_glob)
    assert output == """Más allá de las buenas intenciones, una dictadura es una dictadura.

¿Cómo es que te parece nerd lo bello? Gaaaaaay
"""

    shutil.rmtree(pofiles_dirpath)
