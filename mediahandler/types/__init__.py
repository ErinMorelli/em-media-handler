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
'''Media types module'''


# ======== IMPORT MODULES ======== #

import logging
from os import path
from re import search
from subprocess import Popen, PIPE


# ======== VIDEO CLASS ======== #

class Media(object):
    '''Media handler parent class'''

    # ======== SET GLOBAL CLASS OPTIONS ======== #

    def __init__(self, settings, push):
        '''Init media class'''
        self.type = type(self).__name__.lower()
        # Input
        self.settings = settings
        self.push = push
        # Filebot
        self.filebot = {
            'bin': '/usr/bin/filebot',
            'action': 'copy',
            'db': '',
            'format': '',
            'flags': ['-non-strict', '-no-analytics']
        }
        # Type specific
        self.dst_path = ''

    # ======== GET VIDEO ======== #

    def add(self, file_path):
        '''A new media file'''
        logging.info("Starting %s information handler", self.type)
        # Check for custom path in settings
        if self.settings['folder'] != '':
            if path.exists(self.settings['folder']):
                self.dst_path = self.settings['folder']
                logging.debug("Using custom path: %s", self.dst_path)
        # Set up query
        m_cmd = [self.filebot['bin'],
                 '-rename', file_path,
                 '--db', self.filebot['db'],
                 '--format', self.filebot['format'],
                 '--action', self.filebot['action']]
        m_cmd.extend(self.filebot['flags'])
        # Get info
        return self.__media_info(m_cmd, file_path)

    # ======== GET VIDEO INFO FROM FILEBOT ======== #

    def __media_info(self, cmd, file_path):
        '''Get video info from filebot'''
        logging.info("Getting %s information", self.type)
        # Process query
        query = Popen(cmd, stdout=PIPE)
        # Get output
        (output, err) = query.communicate()
        logging.debug("Query output: %s", output)
        logging.debug("Query return errors: %s", err)
        # Process output
        return self.process_output(output, file_path)

    # ======== PROCESS FILEBOT OUTPUT ======== #

    def process_output(self, output, file_path):
        '''Check for good response or skipped content'''
        logging.info("Processing query output")
        new_file = None
        skipped = False
        # Set up regexes
        action = self.filebot['action'].upper()
        good_query = r"\[%s\] Rename \[.*\] to \[(.*)\]" % action
        skip_query = r"Skipped \[(.*)\] because \[(.*)\] already exists"
        # Look for content
        get_good = search(good_query, output)
        get_skip = search(skip_query, output)
        # Check return
        if get_good is not None:
            new_file = get_good.group(1)
        elif get_skip is not None:
            skipped = True
            new_file = get_skip.group(2)
            logging.warning("Duplicate file was skipped: %s", new_file)
        # Check for failure
        if new_file is None:
            return self.__match_error(file_path)
        # Return info
        logging.debug("New file: %s", new_file)
        return new_file, skipped

    # ======== MATCH ERROR ======== #

    def __match_error(self, name):
        '''Return a match error'''
        return self.push.failure("Unable to match %s: %s" % (self.type, name))
