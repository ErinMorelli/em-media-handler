#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2015 Erin Morelli
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
'''Initialize module'''


import _common
from _common import unittest
from _common import MHTestSuite

import mediahandler.util.notify as Notify


class PushObjectTests(unittest.TestCase):

    def setUp(self):
        # Testing name
        self.name = "push-{0}".format(_common.get_test_id())
        # Settings
        args = _common.get_pushover_api()
        args['enabled'] = True
        args['notify_name'] = ''
        # Push object
        self.push = Notify.Push(args)
        # Disable push
        self.push.disable = True

    def test_new_push_object(self):
        # Dummy settings
        args = {'name': self.name}
        # Make object
        new_obj = Notify.Push(args)
        # Check setup
        self.assertDictEqual(new_obj.settings, args)
        self.assertFalse(new_obj.disable)

    def test_new_push_options(self):
        # Dummy settings
        args = {'name': self.name}
        # Make object
        new_obj = Notify.Push(args, True)
        # Check setup
        self.assertDictEqual(new_obj.settings, args)
        self.assertTrue(new_obj.disable)

    def test_send_msg_bad(self):
        # Enable push
        self.push.disable = False
        # Bad API settings
        self.push.settings['api_key'] = _common.random_string(30)
        self.push.settings['user_key'] = _common.random_string(30)
        # Message
        msg = _common.random_string(10)
        # Send message
        resp = self.push.send_message(msg)
        # Check response
        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.reason, 'Bad Request')

    def test_send_msg_good(self):
        # Enable push
        self.push.disable = False
        # Message
        msg = _common.random_string(10)
        # Send message
        resp = self.push.send_message(msg)
        # Check response
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.reason, 'OK')

    def test_success_both_empty(self):
        # Set up test
        file_array = []
        skipped = []
        # Run test
        regex = r'No files or skips found to notify about'
        self.assertRaisesRegexp(
            SystemExit, regex, self.push.success, file_array, skipped)

    def test_success_empty_skips(self):
        # Set up test
        file_array = [self.name]
        skipped = []
        # Run test
        result = self.push.success(file_array, skipped)
        regex = r'Media was successfully added to your server:\n\+ {0}'.format(
            self.name)
        self.assertRegexpMatches(result, regex)

    def test_success_empty_files(self):
        # Set up test
        file_array = []
        skipped = [self.name]
        # Run test
        result = self.push.success(file_array, skipped)
        regex = r'Some files were skipped:\n\- {0}'.format(self.name)
        self.assertRegexpMatches(result, regex)

    def test_success_all(self):
        # Enable push
        self.push.disable = False
        self.push.settings['notify_name'] = 'test'
        # Generate a 2nd name
        skips = "skip-{0}".format(_common.get_test_id())
        # Set up test
        file_array = [self.name]
        skipped = [skips]
        # Run test
        result = self.push.success(file_array, skipped)
        reg1 = r'Media was successfully added to your server:\n\+ {0}'.format(
            self.name)
        reg2 = r'Some files were skipped:\n\- {0}'.format(skips)
        regex = r'{0}\n\n{1}'.format(reg1, reg2)
        self.assertRegexpMatches(result, regex)

    def test_failure_normal(self):
        # Enable push
        self.push.disable = False
        # Set up test
        msg = _common.random_string(10)
        # Run test
        self.assertRaisesRegexp(
            SystemExit, msg, self.push.failure, msg)

    def test_failure_usage(self):
        # Set up test
        msg = _common.random_string(10)
        # Run test
        self.assertRaisesRegexp(
            SystemExit, '2', self.push.failure, msg, True)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2, buffer=True)
