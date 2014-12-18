#!/usr/bin/python
#
# This file is a part of EM Media Handler
# Copyright (c) 2014 Erin Morelli
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
import mediahandler.util.args as Args


# ======== PUSH CLASS DECLARTION ======== #

class Push(object):
    '''Push notification class'''
    # ======== INIT NOTIFY CLASS ======== #

    def __init__(self, settings, is_deluge=False, disable=False):
        '''Initialize push notifications'''
        logging.info("Initializing notification class")
        self.settings = settings
        self.is_deluge = is_deluge
        self.disable = disable

    # ======== SEND MESSAGE VIA PUSHOVER ======== #

    def send_message(self, conn_msg):
        '''Send message'''
        logging.info("Sending push notification")
        # Initialize connection with pushover
        conn = HTTPSConnection("api.pushover.net:443")
        # Set default title
        conn_title = "EM Media Handler"
        # Look for custom notify name
        if self.settings['notify_name'] != '':
            conn_title = self.settings['notify_name']
        # Encode request URL
        conn_url = urlencode({
            "token": self.settings['api_key'],
            "user": self.settings['user_key'],
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
        # Check for response success
        if conn_resp != 200:
            logging.error("API Response: %s %s",
                          conn_resp.status, conn_resp.reason)
        else:
            logging.info("API Response: %s %s",
                         conn_resp.status, conn_resp.reason)
        logging.debug("After push notification send")

    # ======== SET SUCCESS INFO ======== #

    def success(self, file_array, skipped=None):
        '''Success notification'''
        logging.info("Starting success notifications")
        # Set success message
        conn_text = ''
        # Check for added files
        if len(file_array) > 0:
            media_list = '\n    '.join(file_array)
            conn_text = '''Media was successfully added to your server:
    %s
''' % media_list
        # Set skipped message if set
        if skipped is not None and len(skipped) > 0:
            skipped_list = '\n    '.join(skipped)
            skipped_msg = '''Some files were skipped:
    %s
''' % skipped_list
            if conn_text == '':
                conn_text = skipped_msg
            else:
                conn_text = conn_text + '\n' + skipped_msg
        # Check there's a message to send
        if conn_text == '':
            logging.warning("No files or skips found to notify about")
            sys.exit(1)
        # If push notifications enabled
        if self.settings['enabled'] and not self.disable:
            # Send message
            self.send_message(conn_text)
        # If via CLI, print a message as well
        if not self.is_deluge:
            print "\n" + conn_text
        # Exit
        logging.warning(conn_text)
        sys.exit(1)

    # ======== SET ERROR INFO & EXIT ======== #

    def failure(self, error_details, usage=False):
        '''Failure notification'''
        logging.info("Starting failure notifications")
        # Set error message
        conn_text = '''There was an error reported:
%s
        ''' % error_details
        # If push notifications enabled
        if self.settings['enabled'] and not self.disable:
            # Send message
            self.send_message(conn_text)
        # Raise python warning
        logging.warning(error_details)
        if usage:
            Args.show_usage(2, error_details)
        else:
            print "\nERROR: %s\n" % error_details
            sys.exit(2)
