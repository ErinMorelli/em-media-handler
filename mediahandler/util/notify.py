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

    - |MHPush|
        An object which contains the all the logic for sending
        push notifications and raising errors produced by mediahandler.

'''

import logging
import sys
import requests
from json import dumps

import mediahandler as mh
import mediahandler.util.args as Args


class MHPush(mh.MHObject):
    '''An object which contains the all the logic for sending
    push notifications and raising errors produced by mediahandler.

    Arguments:
        - settings
            Required. Dict or MHSettings object.
        - disable
            True/False.

    Public methods:

        - |send_message()|
            Wrapper function for sending push notification
            messages via various 3rd party services.

        - |success()|
            A wrapper for send_message() which sends a success
            message and returns message content.

        - |failure()|
            A wrapper for send_message() which sends a failure
            message and raises a SystemExit.
    '''

    def __init__(self, settings, disable=False):
        '''Initializes the MHPush object.

        Arguments:

            - settings
                Required. Dict or MHSettings object containing
                push notification-specific settings.

            - disable
                True/False. Defaults to False. Enables/disables push
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
        if hasattr(self.pushover, 'session'):
            self._send_pushover(conn_msg, conn_title)

        # Send to pushbullet
        if hasattr(self.pushbullet, 'session'):
            self._send_pushbullet(conn_msg, conn_title)

        return

    def success(self, file_array, skipped=None):
        '''Builds and sends a success notification.

        Arguments:

            - file_array
                Required. An array of the files added via the
                mediahandler.handler.add_media() function.

            - skipped
                Defaults to None. An array of any files that were
                skipped during the add_media() sequence.
        '''

        logging.info("Starting success notifications")

        # Set success message
        conn_text = ''
        conn_title = 'Media Added'

        # Check for added files
        if len(file_array) > 0:
            media_list = '\n+ '.join(file_array)
            conn_text = '+ {0}\n'.format(media_list)

        # Set skipped message if set
        if skipped is not None and len(skipped) > 0:
            skipped_list = '\n- '.join(skipped)
            skipped_msg = 'Skipped files:\n- {0}\n'.format(skipped_list)

            # Append to existing message, if needed
            if conn_text == '':
                conn_text = skipped_msg
            else:
                conn_text = '{0}\n{1}'.format(conn_text, skipped_msg)

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

            - error_details
                String. A message detailing the error that
                was reported during the add_media() sequence.
        '''

        logging.info("Starting failure notifications")

        # Set error message
        conn_title = 'Error Reported'

        # Send message
        self.send_message(error_details, conn_title)

        # Log warning 
        logging.error(error_details)

        self.parser.error(error_details)

    # 3rd party API requests function

    def _make_request(self, session, url, method='GET', params=None):
        '''Makes an API request to the provided session object
        '''

        # Retrieve method function instance from session
        req = getattr(session, method.lower())

        # Make request
        resp = req(url, data=params)

        # Get JSON request response
        conn_resp = resp.json()
        logging.debug(conn_resp)

        # Check for response success
        if resp.status_code is not 200:
            logging.error(
                "%s %s: %s %s",
                method, url, resp.status_code, resp.reason)

        return conn_resp

    # 3rd party API credential validation functions

    def _validate_credentials(self):
        '''Wrapper for validating API credentials for 3rd party services.
        '''

        # Pushover
        if self.pushover.api_key is not None:
            self._validate_pushover()

        # Pushbullet
        if self.pushbullet.token is not None:
            self._validate_pushbullet()

        return

    def _validate_pushover(self):
        '''Validates Pushover API credentials.
        '''

        logging.debug("Validating Pushover credentials")

        # Set up request params
        self.pushover.url = {
            'token': self.pushover.api_key,
            'user': self.pushover.user_key,
        }

        # Create pushover session object
        self.pushover.session = requests.Session()
        self.pushover.session.headers.update({
           'Content-type': 'application/x-www-form-urlencoded'
        })

        # Make request
        resp = self._make_request(
            self.pushover.session,
            'https://api.pushover.net/1/users/validate.json',
            'POST',
            self.pushover.url
        )

        # Check result
        if not resp['status']:
            error_msg = 'Pushover: {0}'.format(resp['errors'][0])
            logging.error(error_msg)
            self.parser.error(error_msg)

        # Return success
        logging.info("Pushover API credentials successfully validated")

        return True

    def _validate_pushbullet(self):
        '''Validates Pushbullet API credentials.
        '''

        logging.debug("Validating Pushbullet credentials")

        # Create pushover session object with credentials
        self.pushbullet.session = requests.Session()
        self.pushbullet.session.auth = (self.pushbullet.token, '')
        self.pushbullet.session.headers.update({
            'Content-Type': 'application/json'
        })

        # Make request
        resp = self._make_request(
            self.pushbullet.session,
            'https://api.pushbullet.com/v2/users/me'
        )

        # Check result
        if 'error' in resp.keys():
            error_msg = 'Pushbullet: {0}'.format(resp['error']['message'])
            logging.error(error_msg)
            self.parser.error(error_msg)

        # Return success
        logging.info("Pushbullet API credentials successfully validated")

        return True

    # 3rd party API send functions

    def _send_pushover(self, conn_msg, conn_title):
        '''Sends a message via the Pushover API.
        '''

        logging.debug("Sending Pushover notification")

        # Add values to request URL & encode
        self.pushover.url["title"] = conn_title
        self.pushover.url["message"] = conn_msg

        # Make request
        resp = self._make_request(
            self.pushover.session,
            'https://api.pushover.net/1/messages.json',
            'POST',
            self.pushover.url
        )

        return resp

    def _send_pushbullet(self, conn_msg, conn_title):
        '''Sends a message via the Pushbullet API.
        '''

        logging.debug("Sending Pushbullet notification")

        # Set up json request data
        request_data = dumps({
            'type': 'note',
            'title': conn_title,
            'body': conn_msg,
        })

        # Make request
        resp = self._make_request(
            self.pushbullet.session,
            'https://api.pushbullet.com/v2/pushes',
            'POST',
            request_data,
        )

        return resp
