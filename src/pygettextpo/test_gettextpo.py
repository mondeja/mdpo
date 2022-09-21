# Copyright Canonical Ltd.  This software is licensed under the GNU
# Affero General Public License version 3 (see the file LICENSE).

import os
import sys
import unittest

import gettextpo


dist_folder = os.path.join(os.path.dirname(__file__), 'dist')
if dist_folder not in sys.path:
    sys.path.insert(0, dist_folder)


class PoMessageGettersTestCase(unittest.TestCase):
    def testGetSetMsgId(self):
        msg = gettextpo.PoMessage()
        self.assertIs(msg.msgid, None)

        msg.set_msgid(b'Hello')
        self.assertEqual(msg.msgid, b'Hello')

        msg.set_msgid(None)
        self.assertIs(msg.msgid, None)

    def testGetSetMsgStr(self):
        msg = gettextpo.PoMessage()
        self.assertIs(msg.msgstr, None)

        msg.set_msgstr(b'Hello')
        self.assertEqual(msg.msgstr, b'Hello')

        msg.set_msgstr(None)
        self.assertIs(msg.msgstr, None)

    def testGetSetMsgStrPlural(self):
        msg = gettextpo.PoMessage()
        self.assertEqual(msg.msgstr_plural, [])

        msg.set_msgstr_plural(b'Hello')
        self.assertEqual(msg.msgstr_plural, b'Hello')

        msg.set_msgstr_plural(None)
        self.assertEqual(msg.msgstr_plural, [])


"""

class PoFileTestCase(unittest.TestCase):

    def testCreateEmpty(self):
        # Test that we can create an empty pofile object
        pofile = gettextpo.PoFile()
        self.assertEqual(list(iter(pofile)), [])

    def testAddMessage(self):
        # Test that we can add messages to a new pofile object
        pofile = gettextpo.PoFile()
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Hello')
        poiter = iter(pofile)
        poiter.insert(msg)

        self.assertEqual(list(iter(pofile)), [msg])

    def testAddMessageTwiceFails(self):
        # A message object can only be added to one pofile object
        pofile1 = gettextpo.PoFile()
        pofile2 = gettextpo.PoFile()
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Hello')

        poiter = iter(pofile1)
        poiter.insert(msg)

        poiter = iter(pofile2)
        self.assertRaises(ValueError, poiter.insert, msg)

    def testAddMessages(self):
        pofile = gettextpo.PoFile()
        msg1 = gettextpo.PoMessage()
        msg1.set_msgid(b'Foo')
        msg2 = gettextpo.PoMessage()
        msg2.set_msgid(b'Bar')

        poiter = iter(pofile)
        poiter.insert(msg1)
        poiter.insert(msg2)

        self.assertEqual(list(iter(pofile)), [msg1, msg2])


class PoMessageTestCase(unittest.TestCase):

    def testCreateMessage(self):
        # Test that messages can be created.
        msg = gettextpo.PoMessage()

    def testSetMsgId(self):
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Hello')
        self.assertEqual(msg.msgid, b'Hello')
        msg.set_msgid_plural(b'Hellos')
        self.assertEqual(msg.msgid_plural, b'Hellos')

    def testSetMsgCtxt(self):
        msg = gettextpo.PoMessage()
        msg.set_msgctxt(b'Hello')
        self.assertEqual(msg.msgctxt, b'Hello')

    def testSetMsgStr(self):
        msg = gettextpo.PoMessage()
        msg.set_msgstr(b'Hello World')
        self.assertEqual(msg.msgstr, b'Hello World')

    def testGetMsgStr(self):
        msg1 = gettextpo.PoMessage()
        msg1.set_msgid(b'Hello')
        msg1.set_msgstr(b'Hola')
        self.assertEqual(msg1.msgstr, b'Hola')

        msg2 = gettextpo.PoMessage()
        msg2.set_msgid(b'Hello')
        self.assertEqual(msg2.msgstr, None)

    def testSetMsgStrPlural(self):
        # Test handling of plural msgstrs.  The PoMessage object can
        # not hold plural msgstrs if the msgid does not have a plural.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Something')
        self.assertRaises(ValueError, msg.set_msgstr_plural, 0, b'Zero')
        self.assertEqual(msg.msgstr_plural, [])

        # need to set the plural msgid first, then add the plural msgstrs
        msg.set_msgid_plural(b'Somethings')
        msg.set_msgstr_plural(0, b'Zero')
        msg.set_msgstr_plural(1, b'One')
        msg.set_msgstr_plural(2, b'Two')
        self.assertEqual(msg.msgstr_plural, [b'Zero', b'One', b'Two'])


class CheckFormatTestCase(unittest.TestCase):

    def assertGettextPoError(self, expected_errors, msg):
        with self.assertRaises(gettextpo.error) as raised:
            msg.check_format()
        self.assertEqual(expected_errors, raised.exception.error_list)
        self.assertEqual(
            "\n".join(message for _, _, message in expected_errors),
            str(raised.exception))

    def testGoodFormat(self):
        # Check that no exception is raised on a good translation.

        # A translation may use different format characters while still
        # being valid.  For example, both "%f" and "%g" can be used to
        # format a floating point value, so no error should be raised on
        # that kind of change.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Hello %s %d %g')
        msg.set_format('c-format', True)
        msg.set_msgstr(b'Bye %s %.2d %f')

        # this should run without an exception
        msg.check_format()

    def testAddFormatSpec(self):
        # Test that an exception is raised when a format string is added.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'No format specifiers')
        msg.set_format('c-format', True)
        msg.set_msgstr(b'One format specifier: %20s')
        expected_errors = [
            ("error", 0,
             "number of format specifications in 'msgid' and 'msgstr' does "
             "not match"),
            ]
        self.assertGettextPoError(expected_errors, msg)

    def testSwapFormatSpecs(self):
        # Test that an exception is raised when format strings are transposed.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Spec 1: %s, Spec 2: %d')
        msg.set_format('c-format', True)
        msg.set_msgstr(b'Spec 1: %d, Spec 2: %s')
        expected_errors = [
            ("error", 0,
             "format specifications in 'msgid' and 'msgstr' for argument 1 "
             "are not the same"),
            ("error", 0,
             "format specifications in 'msgid' and 'msgstr' for argument 2 "
             "are not the same"),
            ]
        self.assertGettextPoError(expected_errors, msg)

    def testNonFormatString(self):
        # Test that no exception is raised if the message is not marked as
        # a format string.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Spec 1: %s, Spec 2: %d')
        msg.set_format('c-format', False)
        msg.set_msgstr(b'Spec 1: %d, Spec 2: %s')

        # this should run without an exception
        msg.check_format()

    def testEmptyMsgStr(self):
        # Test that empty translations do not trigger a failure.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'Hello %s')
        msg.set_format('c-format', True)
        msg.set_msgstr(None)

        # this should run without an exception
        msg.check_format()

    def testGoodPlural(self):
        # Test that a good plural message passes without error.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'%d apple')
        msg.set_msgid_plural(b'%d apples')
        msg.set_format('c-format', True)
        msg.set_msgstr_plural(0, b'%d orange')
        msg.set_msgstr_plural(1, b'%d oranges')
        msg.set_msgstr_plural(2, b'%d oranges_')

        # this should run without an exception
        msg.check_format()

    def testBadPlural(self):
        # Test that bad plural translations raise an error error.
        msg = gettextpo.PoMessage()
        msg.set_msgid(b'%d apple')
        msg.set_msgid_plural(b'%d apples')
        msg.set_format('c-format', True)
        msg.set_msgstr_plural(0, b'%d orange')
        msg.set_msgstr_plural(1, b'%d oranges')
        msg.set_msgstr_plural(2, b'%g oranges_')
        expected_errors = [
            ("error", 0,
             "format specifications in 'msgid_plural' and 'msgstr[2]' for "
             "argument 1 are not the same"),
            ]
        self.assertGettextPoError(expected_errors, msg)

    def testUnicodeString(self):
        # Test that a translation with unicode chars is working.
        msg = gettextpo.PoMessage()
        msg.set_msgid(u'Carlos Perell\xf3 Mar\xedn')
        msg.set_msgstr(u'Carlos Perell\xf3 Mar\xedn')
        self.assertEqual(msg.msgid, b'Carlos Perell\xc3\xb3 Mar\xc3\xadn')
        self.assertEqual(msg.msgstr, b'Carlos Perell\xc3\xb3 Mar\xc3\xadn')

## XXXX - gettext doesn't seem to check for this one
#
#    def testBadPluralMsgId(self):
#        # Test that conflicting plural msgids raise errors on their own.
#        msg = gettextpo.PoMessage()
#        msg.set_msgid(b'%d apple')
#        msg.set_msgid_plural(b'%g apples')
#        msg.set_format('c-format', True)
#        self.assertRaises(gettextpo.error, msg.check_format)
#
"""

if __name__ == '__main__':
    unittest.main()
