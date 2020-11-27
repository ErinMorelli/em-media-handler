#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2020 Erin Morelli
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
"""Initialize module"""

import responses

import tests.common as common
from tests.common import unittest
from tests.common import MHTestSuite

import mediahandler.util.notify as Notify


class PushObjectTests(unittest.TestCase):

    def setUp(self):
        # Testing name
        self.name = "push-{0}".format(common.get_test_id())
        # Settings
        self.args = {
            'enabled': True,
            'notify_name': '',
            'pushover': common.get_pushover_api(),
            'pushbullet': common.get_pushbullet_api()
        }
        # Push object
        self.push = None
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET,
                     'https://api.pushbullet.com/v2/users/me',
                     json={'iden': 'iden', 'title': 'title', 'body': 'body'},
                     status=200)
            rsps.add(responses.POST,
                     'https://api.pushover.net/1/users/validate.json',
                     json={'status': 1},
                     status=200)
            self.push = Notify.MHPush(self.args)
        # Disable push
        self.push.disable = True

    @responses.activate
    def test_bad_po_credentials(self):
        responses.add(responses.POST,
                      'https://api.pushover.net/1/users/validate.json',
                      json={
                          'errors': [
                              'application token is invalid'
                          ],
                          'status': 0
                      },
                      status=400)
        # Deactivate PB
        self.args['pushbullet']['token'] = None
        # Run test
        regex = r'Pushover: application token is invalid'
        self.assertRaisesRegexp(SystemExit, regex, Notify.MHPush, self.args)

    @responses.activate
    def test_bad_pb_credentials(self):
        responses.add(responses.GET,
                      'https://api.pushbullet.com/v2/users/me',
                      json={
                          'error': {
                              'message': 'Access token is missing or invalid.'
                          }
                      },
                      status=400)
        # Deactivate PO
        self.args['pushover']['api_key'] = None
        # Run test
        regex = r'Pushbullet: Access token is missing or invalid.'
        self.assertRaisesRegexp(SystemExit, regex, Notify.MHPush, self.args)

    def test_new_push_object(self):
        # Dummy settings
        args = {
            'enabled': False,
            'name': self.name
        }
        # Make object
        new_obj = Notify.MHPush(args, True)
        # Check setup
        self.assertEqual(new_obj.name, self.name)
        self.assertTrue(new_obj.disable)

    @responses.activate
    def test_send_pomsg_bad(self):
        responses.add(responses.POST,
                      'https://api.pushover.net/1/messages.json',
                      json={'errors': ['not found'], 'status': 0},
                      status=400)
        # Bad API settings
        self.push.pushover.url['token'] = common.random_string(30)
        self.push.pushover.url['user'] = common.random_string(30)
        # Message
        msg = common.random_string(10)
        title = common.random_string(10)
        # Send message
        resp = self.push._send_pushover(msg, title)
        # Check response
        self.assertFalse(resp['status'])
        self.assertIn('errors', resp.keys())

    @responses.activate
    def test_send_pomsg_good(self):
        responses.add(responses.POST,
                      'https://api.pushover.net/1/messages.json',
                      json={'status': 1},
                      status=200)
        # Message
        msg = common.random_string(10)
        title = common.random_string(10)
        # Send message
        resp = self.push._send_pushover(msg, title)
        # Check response
        self.assertTrue(resp['status'])

    @responses.activate
    def test_send_pbmsg_bad(self):
        responses.add(responses.POST,
                      'https://api.pushbullet.com/v2/pushes',
                      json={'error': 'not found'},
                      status=400)
        # Bad API settings
        self.push.pushbullet.session.auth = (common.random_string(30), '')
        # Message
        msg = common.random_string(10)
        title = common.random_string(10)
        # Send message
        resp = self.push._send_pushbullet(msg, title)
        # Check response
        self.assertIn('error', resp.keys())

    @responses.activate
    def test_send_pbmsg_good(self):
        # Message
        msg = common.random_string(10)
        title = common.random_string(10)
        # Set up response
        responses.add(responses.POST,
                      'https://api.pushbullet.com/v2/pushes',
                      json={'iden': 'iden', 'title': title, 'body': msg},
                      status=200)
        # Send message
        resp = self.push._send_pushbullet(msg, title)
        # Check response
        self.assertIn('iden', resp.keys())
        self.assertEqual(resp['title'], title)
        self.assertEqual(resp['body'], msg)

    def test_send_msg_good_title(self):
        # Message
        msg = common.random_string(10)
        # Send message
        resp = self.push.send_message(msg)
        # Check response
        self.assertIsNone(resp)

    def test_success_both_empty(self):
        # Set up test
        file_array = []
        skipped = []
        # Run test
        regex = r'No files or skips found to notify about'
        self.assertRaisesRegexp(
            SystemExit, regex, self.push.success, file_array, skipped)

    @responses.activate
    def test_success_empty_skips(self):
        responses.add(responses.POST,
                      'https://api.pushbullet.com/v2/pushes',
                      json={'iden': 'iden', 'title': 'title', 'body': 'body'},
                      status=200)
        responses.add(responses.POST,
                      'https://api.pushover.net/1/messages.json',
                      json={'status': 1},
                      status=200)
        # Set up test
        file_array = [self.name]
        skipped = []
        # Run test
        result = self.push.success(file_array, skipped)
        regex = r'\+ {0}'.format(self.name)
        self.assertRegexpMatches(result, regex)

    @responses.activate
    def test_success_empty_files(self):
        responses.add(responses.POST,
                      'https://api.pushbullet.com/v2/pushes',
                      json={'iden': 'iden', 'title': 'title', 'body': 'body'},
                      status=200)
        responses.add(responses.POST,
                      'https://api.pushover.net/1/messages.json',
                      json={'status': 1},
                      status=200)
        # Set up test
        file_array = []
        skipped = [self.name]
        # Run test
        result = self.push.success(file_array, skipped)
        regex = r'Skipped files:\n\- {0}'.format(self.name)
        self.assertRegexpMatches(result, regex)

    @responses.activate
    def test_success_all(self):
        # Set up responses
        responses.add(responses.POST,
                      'https://api.pushbullet.com/v2/pushes',
                      json={'iden': 'iden', 'title': 'title', 'body': 'body'},
                      status=200)
        responses.add(responses.POST,
                      'https://api.pushover.net/1/messages.json',
                      json={'status': 1},
                      status=200)
        # Enable push
        self.push.disable = False
        self.push.notify_name = 'test'
        # Generate a 2nd name
        skips = "skip-{0}".format(common.get_test_id())
        # Set up test
        file_array = [self.name]
        skipped = [skips]
        # Run test
        result = self.push.success(file_array, skipped)
        reg1 = r'\+ {0}'.format(
            self.name)
        reg2 = r'Skipped files:\n\- {0}'.format(skips)
        regex = r'{0}\n\n{1}'.format(reg1, reg2)
        self.assertRegexpMatches(result, regex)

    def test_failure_normal(self):
        # Enable push
        self.push.disable = False
        # Set up test
        msg = common.random_string(10)
        # Run test
        self.assertRaisesRegexp(
            SystemExit, msg, self.push.failure, msg)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
