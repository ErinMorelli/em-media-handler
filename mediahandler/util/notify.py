#!/usr/bin/python
#
# This file is a part of EM Media Handler
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
'''Notification module'''


# ======== IMPORT MODULES ======== #

import logging
import sys
from json import loads
from urllib import urlencode
from httplib import HTTPSConnection

import mediahandler as mh
import mediahandler.util.args as Args


# ======== PUSH CLASS DECLARTION ======== #

class MHPush(mh.MHObject):
    '''Push notification class'''
    # ======== INIT NOTIFY CLASS ======== #

    def __init__(self, settings, disable=False):
        '''Initialize push notifications'''
        logging.info("Initializing notification class")
        super(MHPush, self).__init__(settings, disable)
        # Set up vars
        self.disable = disable
        self.parser = Args.get_parser()
        # If enabled, check credentials
        if self.enabled:
            self._validate_credentials()

    # ======== VALIDATE CREDENTIALS WRAPPER ======== #

    def _validate_credentials(self):
        '''Wrapper for validating credentials to push services'''
        # Pushover
        self._validate_pushover()
        # Pushbullet
        return

    # ======== VALIDATE PUSHOVER CREDENTIALS ======== #

    def _validate_pushover(self):
        '''Validate pushover api credentials'''
        logging.debug("Validating pushover credentials")
        # Set up request url
        self.pushover.url = {
            "token": self.pushover.api_key,
            "user": self.pushover.user_key,
        }
        conn_url = urlencode(self.pushover.url)
        # Initialize connection with pushover
        self.pushover.conn = HTTPSConnection("api.pushover.net:443")
        # Make request
        self.pushover.conn.request(
            "POST",
            "/1/users/validate.json",
            conn_url,
            {"Content-type": "application/x-www-form-urlencoded"}
        )
        conn_resp = loads(self.pushover.conn.getresponse().read())
        logging.debug(conn_resp)
        # Check result
        if not conn_resp['status']:
            error_msg = 'Pushover: {0}'.format(conn_resp['errors'][0])
            logging.error(error_msg)
            self.parser.error(error_msg)
        # Return success
        logging.info("Pushover API credentials succesfully validated")
        return True

    # ======== SEND MESSAGE VIA PUSHOVER ======== #

    def _send_pushover(self, conn_msg, msg_title=None):
        '''Send message via pushover'''
        logging.debug("Sending pushover notification")
        # Set default title
        conn_title = "EM Media Handler"
        # Look for custom notify name
        if self.notify_name is not None:
            conn_title = self.notify_name
        # Look for message title
        if msg_title is not None:
            conn_title = '{0}: {1}'.format(conn_title, msg_title)
        # Encode request URL
        self.pushover.url["title"] = conn_title,
        self.pushover.url["message"] = conn_msg
        conn_url = urlencode(self.pushover.url)
        logging.debug("API call: %s", conn_url)
        # Send API request
        self.pushover.conn.request(
            "POST",
            "/1/messages.json",
            conn_url,
            {"Content-type": "application/x-www-form-urlencoded"}
        )
        # Get API response
        conn_resp = self.pushover.conn.getresponse()
        logging.debug(loads(conn_resp.read()))
        # Check for response success
        if conn_resp.status != 200:
            logging.error("API Response: %s %s",
                          conn_resp.status, conn_resp.reason)
        return conn_resp

    # ======== SEND MESSAGE WRAPPER ======== #

    def send_message(self, conn_msg, msg_title=None):
        '''Wrapper for sending push notifcations to multiple sources'''
        # Check if this is enabled
        if not self.enabled or self.disable:
            return
        # Send to pushover
        self._send_pushover(conn_msg, msg_title)
        return

    # ======== SET SUCCESS INFO ======== #

    def success(self, file_array, skipped=None):
        '''Success notification'''
        logging.info("Starting success notifications")
        # Set success message
        conn_text = ''
        conn_title = 'Media Added'
        # Check for added files
        if len(file_array) > 0:
            media_list = '\n + '.join(file_array)
            conn_text = '''Media was successfully added to your server:
+ {0}'''.format(media_list)
        # Set skipped message if set
        if skipped is not None and len(skipped) > 0:
            skipped_list = '\n - '.join(skipped)
            skipped_msg = '''Some files were skipped:
- {0}'''.format(skipped_list)
            if conn_text == '':
                conn_text = skipped_msg
            else:
                conn_text = '{0}\n\n{1}'.format(conn_text, skipped_msg)
            conn_title = '{0} (with Skips)'.format(conn_title)
        # Check there's a message to send
        if conn_text == '':
            logging.warning("No files or skips found to notify about")
            sys.exit("No files or skips found to notify about")
        # Send message
        self.send_message(conn_text, conn_title)
        # Exit
        logging.warning(conn_text)
        return conn_text

    # ======== SET ERROR INFO & EXIT ======== #

    def failure(self, error_details):
        '''Failure notification'''
        logging.info("Starting failure notifications")
        # Set error message
        conn_title = 'Error'
        conn_text = '''There was an error reported:
{0}'''.format(error_details)
        # Send message
        self.send_message(conn_text, conn_title)
        # Raise python warning
        logging.warning(error_details)
        self.parser.error(error_details)
