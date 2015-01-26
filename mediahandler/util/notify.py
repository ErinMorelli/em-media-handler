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
'''
Module: mediahandler.util.notify

Module contains:

    - MHPush -- An object which contains the all the logic for sending
        push notifications and raising errors produced by mediahandler.

'''

import logging
import sys
from json import loads
from urllib import urlencode
from httplib import HTTPSConnection

import mediahandler as mh
import mediahandler.util.args as Args


class MHPush(mh.MHObject):
    '''An object which contains the all the logic for sending
    push notifications and raising errors produced by mediahandler.

    Arguments:
        - settings -- Required. Dict or MHSettings object.
        - disable -- True/False.

    Public methods:

        - send_message() -- Wrapper function for sending push notification
            messages via various 3rd party services.

        - success() -- A wrapper for send_message() which sends a success
            message and returns message content.

        - failure() -- A wrapper for send_message() which sends a failure
            message and raises a SystemExit.
    '''

    def __init__(self, settings, disable=False):
        '''Initializes the MHPush object.

        Arguments:

            - settings -- Required. Dict or MHSettings object containing
                push notification-specific settings.

            - disable -- True/False. Defaults to False. Enables/disables push
                notifications and will return only string messages.
        '''

        logging.info("Initializing notification class")

        # Call super to set object members
        super(MHPush, self).__init__(settings, disable)

        # Set up vars
        self.disable = disable
        self.parser = Args.get_parser()

        # If enabled, check credentials
        if self.enabled:
            self._validate_credentials()

        return

    def send_message(self, conn_msg, msg_title=None):
        '''Wrapper for sending push notifications via 3rd party services.

        The function will exit if the disable flag is set.
        '''

        # Check if this is enabled
        if not self.enabled or self.disable:
            return

        # Set default title
        conn_title = "EM Media Handler"

        # Look for custom notify name
        if self.notify_name is not None:
            conn_title = self.notify_name

        # Look for message title
        if msg_title is not None:
            conn_title = '{0}: {1}'.format(conn_title, msg_title)

        # Send to pushover
        self._send_pushover(conn_msg, conn_title)

        return

    def success(self, file_array, skipped=None):
        '''Builds and sends a success notification.

        Arguments:

            - file_array -- Required. An array of the files added via the
                mediahandler.handler.add_media() function.

            - skipped -- Defaults to None. An array of any files that were
                skipped during the add_media() sequence.
        '''

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

            # Append to existing message, if needed
            if conn_text == '':
                conn_text = skipped_msg
            else:
                conn_text = '{0}\n\n{1}'.format(conn_text, skipped_msg)

            # Set title for skips
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

    def failure(self, error_details):
        '''Builds and sends a failure notification.

        Required argument:

            - error_details -- String. A message detailing the error that
                was reported during the add_media() sequence.
        '''

        logging.info("Starting failure notifications")

        # Set error message
        conn_title = 'Error'
        conn_text = '''There was an error reported:
{0}'''.format(error_details)

        # Send message
        self.send_message(conn_text, conn_title)

        # Log warning 
        logging.error(error_details)

        self.parser.error(error_details)

    # 3rd party API credential validation functions

    def _validate_credentials(self):
        '''Wrapper for validating API credentials for 3rd party services.
        '''

        # Pushover
        self._validate_pushover()

        return

    def _validate_pushover(self):
        '''Validates Pushover API credentials.
        '''

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

        # Get and decode JSON response
        conn_resp = loads(self.pushover.conn.getresponse().read())
        logging.debug(conn_resp)

        # Check result
        if not conn_resp['status']:
            error_msg = 'Pushover: {0}'.format(conn_resp['errors'][0])
            logging.error(error_msg)
            self.parser.error(error_msg)

        # Return success
        logging.info("Pushover API credentials successfully validated")

        return True

    # 3rd party API send functions

    def _send_pushover(self, conn_msg, conn_title):
        '''Sends a message via the Pushover API.
        '''

        logging.debug("Sending pushover notification")

        # Add values to request URL & encode
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
