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
        self.disable = disable
        self.parser = Args.get_parser()

    # ======== SEND MESSAGE VIA PUSHOVER ======== #

    def send_message(self, conn_msg):
        '''Send message'''
        logging.info("Sending push notification")
        # Initialize connection with pushover
        conn = HTTPSConnection("api.pushover.net:443")
        # Set default title
        conn_title = "EM Media Handler"
        # Look for custom notify name
        if self.notify_name is not None:
            conn_title = self.notify_name
        # Encode request URL
        conn_url = urlencode({
            "token": self.api_key,
            "user": self.user_key,
            "title": conn_title,
            "message": conn_msg,
        })
        logging.debug("API call: %s", conn_url)
        # Send API request
        conn.request(
            "POST",
            "/1/messages.json",
            conn_url,
            {"Content-type": "application/x-www-form-urlencoded"}
        )
        # Get API response
        conn_resp = conn.getresponse()
        logging.debug("After push notification send")
        # Check for response success
        if conn_resp.status != 200:
            logging.error("API Response: %s %s",
                          conn_resp.status, conn_resp.reason)
        else:
            logging.info("API Response: %s %s",
                         conn_resp.status, conn_resp.reason)
        return conn_resp

    # ======== SET SUCCESS INFO ======== #

    def success(self, file_array, skipped=None):
        '''Success notification'''
        logging.info("Starting success notifications")
        # Set success message
        conn_text = ''
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
        # Check there's a message to send
        if conn_text == '':
            logging.warning("No files or skips found to notify about")
            sys.exit("No files or skips found to notify about")
        # If push notifications enabled
        if self.enabled and not self.disable:
            # Send message
            self.send_message(conn_text)
        # Exit
        logging.warning(conn_text)
        return conn_text

    # ======== SET ERROR INFO & EXIT ======== #

    def failure(self, error_details):
        '''Failure notification'''
        logging.info("Starting failure notifications")
        # Set error message
        conn_text = '''There was an error reported:
{0}'''.format(error_details)
        # If push notifications enabled
        if self.enabled and not self.disable:
            # Send message
            self.send_message(conn_text)
        # Raise python warning
        logging.warning(error_details)
        self.parser.error(error_details)
