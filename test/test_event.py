import contextlib
import io

from mdpo.md2po import markdown_to_pofile


def test_debug_event():
    md_content = '''# Header

<!-- mdpo-for-translator Comment for translator -->
<!-- mdpo-context foo and bar -->
Content with `span` and [referenced-link][link].

<!-- mdpo-disable-next-line -->
This line will not be extracted.

[link]: https://foo.bar "Title"
'''

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        markdown_to_pofile(
            md_content,
            debug=True,
            command_aliases={
                'mdpo-for-translator': 'translator',
            },
        )
    debug_output = stdout.getvalue()
    
    comparable_debug_output = ''
    for line in debug_output.splitlines(keepends=True):
        if '::' not in line:
            comparable_debug_output += line
            continue
            
        line_split = line.split('::')
        comparable_debug_output += (
            f'{line_split[0]}::<date>::{"::".join(line_split[2:])}'
        )

    expected_output = '''md2po[DEBUG]::<date>::enter_block:: DOC
md2po[DEBUG]::<date>::enter_block:: H - {'level': 1}
md2po[DEBUG]::<date>::text:: Header
md2po[DEBUG]::<date>::leave_block:: H - {'level': 1}
md2po[DEBUG]::<date>::msgid:: msgid='Header'
md2po[DEBUG]::<date>::enter_block:: HTML
md2po[DEBUG]::<date>::text:: <!-- mdpo-for-translator Comment for translator -->
md2po[DEBUG]::<date>::command:: mdpo-translator - Comment for translator (original command: 'mdpo-for-translator')
md2po[DEBUG]::<date>::text:: 

md2po[DEBUG]::<date>::text:: <!-- mdpo-context foo and bar -->
md2po[DEBUG]::<date>::command:: mdpo-context - foo and bar
md2po[DEBUG]::<date>::text:: 

md2po[DEBUG]::<date>::leave_block:: HTML
md2po[DEBUG]::<date>::enter_block:: P
md2po[DEBUG]::<date>::text:: Content with 
md2po[DEBUG]::<date>::enter_span:: CODE
md2po[DEBUG]::<date>::text:: span
md2po[DEBUG]::<date>::leave_span:: CODE
md2po[DEBUG]::<date>::text::  and 
md2po[DEBUG]::<date>::enter_span:: A - {'href': [(<TextType.NORMAL: 0>, 'https://foo.bar')], 'title': [(<TextType.NORMAL: 0>, 'Title')]}
md2po[DEBUG]::<date>::text:: referenced-link
md2po[DEBUG]::<date>::leave_span:: A - {'href': [(<TextType.NORMAL: 0>, 'https://foo.bar')], 'title': [(<TextType.NORMAL: 0>, 'Title')]}
md2po[DEBUG]::<date>::text:: .
md2po[DEBUG]::<date>::leave_block:: P
md2po[DEBUG]::<date>::msgid:: msgid='Content with `span` and [referenced-link][link].' - msgctxt='foo and bar' - tcomment='Comment for translator'
md2po[DEBUG]::<date>::enter_block:: HTML
md2po[DEBUG]::<date>::text:: <!-- mdpo-disable-next-line -->
md2po[DEBUG]::<date>::command:: mdpo-disable-next-line
md2po[DEBUG]::<date>::text:: 

md2po[DEBUG]::<date>::leave_block:: HTML
md2po[DEBUG]::<date>::enter_block:: P
md2po[DEBUG]::<date>::text:: This line will not be extracted.
md2po[DEBUG]::<date>::leave_block:: P
md2po[DEBUG]::<date>::msgid:: msgid='This line will not be extracted.'
md2po[DEBUG]::<date>::leave_block:: DOC
md2po[DEBUG]::<date>::msgid:: msgid=''
md2po[DEBUG]::<date>::link_reference:: target='link' - href='https://foo.bar' - title='Title'
md2po[DEBUG]::<date>::msgid:: msgid='[link]: https://foo.bar "Title"' - msgstr='[link]: https://foo.bar "Title"' - flags='['fuzzy']'
'''
    assert comparable_debug_output == expected_output
