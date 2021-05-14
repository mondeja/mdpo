import io
import sys
from contextlib import redirect_stdout

import md4c
import pytest

from mdpo.command import normalize_mdpo_command
from mdpo.md2po import Md2Po, markdown_to_pofile


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_enter_leave_block_event(abort_event):
    def print_is_task_list_item(self, block, details):
        if block.value == md4c.BlockType.LI:
            sys.stdout.write(str(details['is_task']))

    content = 'Hello\n\n- List item\n- [ ] Another list item\n'

    stdout = io.StringIO()
    md2po = Md2Po(
        content,
        events={
            'enter_block': print_is_task_list_item,
            'leave_block': lambda *_: not abort_event,
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
            'enter_block': lambda *_: not abort_event,
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

    po = markdown_to_pofile(
        content,
        events={
            'enter_span': lambda *_: not abort_event,
            'leave_span': lambda *_: not abort_event,
        },
    )

    assert str(po).splitlines()[4].split('"')[1] == expected_msgid


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_text_event(abort_event):
    content = '<!-- mdpo-disable-codeblocks -->\n'

    md2po = Md2Po(
        content,
        events={
            'text': lambda *_: abort_event,
        },
        include_codeblocks=True,
    )

    md2po.extract()

    # if not text executed, disable codeblocks command is not parsed
    assert md2po.include_codeblocks is not abort_event


@pytest.mark.parametrize(('abort_event'), (True, False))
def test_command_event(abort_event):
    def error_when_unknown_command_event(
        self,
        command,
        comment,
        original_command,
    ):
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
        with pytest.raises(ValueError) as exc:
            md2po.extract()
        assert str(exc.value) == 'unhandled command for testing'
    else:
        md2po.extract()


def test_msgid_event():
    def dont_save_hate_msgid(self, msgid):
        if msgid == 'hate':
            return False

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

    assert output == expected_output
