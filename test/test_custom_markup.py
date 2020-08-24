import string

import pytest

from md2po import markdown_to_pofile

INVALID_CHARACTERS = [' ', '\t', '\n', '"', '\'', '\r', '\\', '\x0b', '\x0c']
SINGLE_CHARACTERS = [
    c for c in string.printable if (not c.isdigit() and
                                    not c.isalpha() and
                                    c not in INVALID_CHARACTERS)
]
DOUBLE_CHARACTERS = ['%s%s' % (c, c) for c in SINGLE_CHARACTERS]
CHARACTERS = SINGLE_CHARACTERS + DOUBLE_CHARACTERS


def build_expected_output(sentence):
    if '\n' in sentence:
        msgid = 'msgid ""'
        for line in sentence.split('\n'):
            msgid += '"%s"' % line
        msgid += 'msgstr ""\n'
    else:
        msgid = '''#\nmsgid ""\nmsgstr ""\n\nmsgid "%s"\nmsgstr ""\n''' % (
            sentence)
    return msgid


@pytest.mark.parametrize('char', CHARACTERS)
def test_bold_string(char):
    content = 'I\'m a text with **bold characters**'
    pofile = markdown_to_pofile(content, bold_string=char, plaintext=False)

    expected_output = build_expected_output(
        'I\'m a text with %sbold characters%s' % (char, char))

    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('char',
                         list(filter(lambda x: '*' not in x, CHARACTERS)))
def test_escape_bold_inside_custom_bold_markup(char):
    content = ('I\'m a text with **bold \\*\\* \\*\\* characters escaped'
               ' and custom %s markups characters unescaped inside**') % (char)
    pofile = markdown_to_pofile(content, bold_string=char,
                                plaintext=False, wrapwidth=200)

    expected_output = build_expected_output(
        'I\'m a text with %sbold ** ** characters escaped'
        ' and custom %s markups characters unescaped inside%s' % (
            char,
            (('\\\\%s' % char) if len(char) == 1 else
             ('\\\\%s\\\\%s' % (char[0], char[1]))),
            char,
        )
    )

    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('char', CHARACTERS)
def test_italic_string(char):
    content = 'I\'m a text with *italic characters*'
    pofile = markdown_to_pofile(content, italic_string=char, plaintext=False)

    expected_output = build_expected_output(
        'I\'m a text with %sitalic characters%s' % (char, char))

    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('char',
                         list(filter(lambda x: '*' not in x, CHARACTERS)))
def test_escape_italic_inside_custom_italic_markup(char):
    content = ('I\'m a text with *italic \\* \\* characters escaped'
               ' and custom %s markups characters unescaped inside*') % (char)
    pofile = markdown_to_pofile(content, italic_string=char,
                                plaintext=False, wrapwidth=200)

    expected_output = build_expected_output(
        'I\'m a text with %sitalic * * characters escaped'
        ' and custom %s markups characters unescaped inside%s' % (
            char,
            (('\\\\%s' % char) if len(char) == 1 else
             ('\\\\%s\\\\%s' % (char[0], char[1]))),
            char,
        )
    )

    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('char', CHARACTERS)
def test_code_string(char):
    content = 'I\'m a text with `inline code`'
    pofile = markdown_to_pofile(content, code_string=char, plaintext=False)

    expected_output = build_expected_output(
        'I\'m a text with %sinline code%s' % (char, char))

    assert pofile.__unicode__() == expected_output


@pytest.mark.parametrize('char',
                         list(filter(lambda x: '`' not in x, CHARACTERS)))
def test_escape_code_inside_custom_code_markup(char):

    content = ('I\'m a text with ``inline code ` ` characters escaped'
               ' and custom %s markups characters unescaped inside``') % (char)
    pofile = markdown_to_pofile(content, code_string=char,
                                plaintext=False, wrapwidth=200)

    expected_output = build_expected_output(
        'I\'m a text with %sinline code ` ` characters escaped'
        ' and custom %s markups characters unescaped inside%s' % (
            char,
            (('\\\\%s' % char) if len(char) == 1 else
             ('\\\\%s\\\\%s' % (char[0], char[1]))),
            char,
        )
    )

    assert pofile.__unicode__() == expected_output
