import io
import re
import sys
from contextlib import redirect_stdout

import md4c
import pytest

from mdpo.command import normalize_mdpo_command
from mdpo.md2po import Md2Po, markdown_to_pofile


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_enter_leave_block_event(abort_event):
    def print_is_task_list_item(
            self,  # noqa: ARG001
            block,
            details,
    ):
        if block is md4c.BlockType.LI:
            sys.stdout.write(str(details['is_task']))

    content = 'Hello\n\n- List item\n- [ ] Another list item\n'

    stdout = io.StringIO()
    md2po = Md2Po(
        content,
        events={
            'enter_block': print_is_task_list_item,
            'leave_block': lambda *_: not abort_event,  # noqa: U101
        },
    )

    with redirect_stdout(stdout):
        md2po.extract()
    assert stdout.getvalue() == 'FalseTrue'

    # if not leave_block executed, uls deep remains at 1
    assert bool(md2po._uls_deep) is abort_event


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_enter_block_event(abort_event):
    content = 'Hello\n'

    md2po = Md2Po(
        content,
        events={
            'enter_block': lambda *_: not abort_event,  # noqa: U101
        },
    )

    md2po.extract()

    assert md2po._current_top_level_block_number == (
        1 if not abort_event else 0
    )


@pytest.mark.parametrize(
    ('abort_event', 'expected_msgid'),
    (
        (True, 'Hello with codespan'),
        (False, 'Hello `with` codespan'),
    ),
)
def test_enter_leave_span_event(abort_event, expected_msgid):
    content = 'Hello `with` codespan'

    pofile = markdown_to_pofile(
        content,
        events={
            'enter_span': lambda *_: not abort_event,  # noqa: U101
            'leave_span': lambda *_: not abort_event,  # noqa: U101
        },
    )

    assert str(pofile).splitlines()[4].split('"')[1] == expected_msgid


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_text_event(abort_event):
    content = '<!-- mdpo-disable-codeblocks -->\n'

    md2po = Md2Po(
        content,
        events={
            'text': lambda *_: abort_event,  # noqa: U101
        },
        include_codeblocks=True,
    )

    md2po.extract()

    # if not text executed, disable codeblocks command is not parsed
    assert md2po.include_codeblocks is not abort_event


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_command_event(abort_event):
    def error_when_unknown_command_event(
        self,  # noqa: ARG001
        command,
        comment,  # noqa: ARG001
        original_command,  # noqa: ARG001
    ):
        # here 'normalize_mdpo_command' is added to simulate a real behaviour,
        # is not related with the test itself
        if normalize_mdpo_command(command) is None and abort_event:
            raise ValueError('unhandled command for testing')

    content = '<!-- mdpo-unknown-command -->'

    md2po = Md2Po(
        content,
        events={
            'command': error_when_unknown_command_event,
        },
    )

    if abort_event:
        expected_msg = 'unhandled command for testing'
        with pytest.raises(ValueError, match=expected_msg):
            md2po.extract()
    else:
        md2po.extract()


def test_command_event_return_false():
    def skip_counter_command_event(
        self,
        command,
        comment,  # noqa: ARG001
        original_command,  # noqa: ARG001
    ):
        if command == 'mdpo-skip':
            self.skip_counter += 1
            return False
        if command == 'mdpo-disable-next-line':
            return False
        return None

    content = '''<!-- mdpo-skip -->

some text

mdpo-skip

<!-- mdpo-othercommand -->
<!-- mdpo-skip -->

<!-- mdpo-disable-next-line -->
This must be included in output
'''

    # Md2Po must be subclassed because is defined with fixed slots
    class CustomMd2Po(Md2Po):
        def __init__(self, *args, **kwargs):
            self.skip_counter = 0
            super().__init__(*args, **kwargs)

    md2po = CustomMd2Po(
        content,
        events={
            'command': skip_counter_command_event,
        },
    )
    output = md2po.extract()

    assert md2po.skip_counter == content.count('<!-- mdpo-skip -->')
    assert output == '''#
msgid ""
msgstr ""

msgid "some text"
msgstr ""

msgid "mdpo-skip"
msgstr ""

msgid "This must be included in output"
msgstr ""
'''


def test_msgid_event():
    def dont_save_hate_msgid(self, msgid, *args):  # noqa: ARG001
        if msgid == 'hate':
            return False
        return None

    content = '''<!-- mdpo-disable-next-line -->
hate

love

equilibrium
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "equilibrium"
msgstr ""
'''

    output = markdown_to_pofile(
        content,
        events={
            'msgid': dont_save_hate_msgid,
        },
    )

    assert str(output) == expected_output


def test_link_reference_event():
    def process_footnotes(self, target, href, title):  # noqa: ARG001
        if re.match(r'^\^\d', target):
            return False
        return None

    content = '''This is a footnote[^1]. This is another[^2].

Here is a [link reference][foo].

[^1]: This is a footnote content.

[^2]: This is another footnote content.

[foo]: https://github.com/mondeja/mdpo
'''

    expected_output = '''#
msgid ""
msgstr ""

msgid "This is a footnote[^1]. This is another[^2]."
msgstr ""

msgid "Here is a [link reference][foo]."
msgstr ""

msgid "[^1]: This is a footnote content."
msgstr ""

msgid "[^2]: This is another footnote content."
msgstr ""

#, fuzzy
msgid "[foo]: https://github.com/mondeja/mdpo"
msgstr "[foo]: https://github.com/mondeja/mdpo"
'''

    output = markdown_to_pofile(
        content,
        events={
            'link_reference': process_footnotes,
        },
    )

    assert str(output) == expected_output
