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
from urllib import urlencode
from httplib import HTTPSConnection


# ======== PUSH CLASS DECLARTION ======== #

class Push:
    '''Push notification class'''
    # ======== INIT NOTIFY CLASS ======== #

    def __init__(self, settings):
        '''Initialize push notifications'''
        logging.info("Initializing notification class")
        self.settings = settings

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

    def success(self, file_array):
        '''Success notification'''
        logging.info("Starting success notifications")
        # Format file list
        media_list = '\n    '.join(file_array)
        # Set success message
        conn_text = '''Media was successfully added to your server:
%s
        ''' % media_list
        # If push notifications enabled
        if self.settings['enabled']:
            # Send message
            self.__send_message(conn_text)
        logging.warning(conn_text)

    # ======== SET ERROR INFO & EXIT ======== #

    def failure(self, error_details):
        '''Failure notification'''
        logging.info("Starting failure notifications")
        # Set error message
        conn_text = '''There was an error reported:
%s
        ''' % error_details
        # If push notifications enabled
        if self.settings['enabled']:
            # Send message
            self.__send_message(conn_text)
        # Raise python warning
        logging.warning(error_details)
        raise Warning(error_details)
