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
'''Media types module'''


# ======== IMPORT MODULES ======== #

import os
import logging
from re import findall, search
from subprocess import Popen, PIPE


# ======== VIDEO CLASS ======== #

class Media(object):
    '''Media handler parent class'''

    # ======== SET GLOBAL CLASS OPTIONS ======== #

    def __init__(self, settings, push):
        '''Init media class'''
        self.type = type(self).__name__.lower()
        if not hasattr(self, 'ptype'):
            self.ptype = 'Media'
        # Input
        self.settings = settings
        self.push = push
        # Filebot
        self.filebot = {
            'action': 'copy',
            'db': '',
            'format': '',
            'flags': '-non-strict',
        }
        # Check for filebot
        if 'has_filebot' in self.settings.keys():
            self.filebot['bin'] = self.settings['has_filebot']
        # Type specific
        self.dst_path = '%s/Media/%s' % (os.path.expanduser("~"), self.ptype)
        # Check for custom path in settings
        if 'folder' in self.settings.keys() and self.ptype is not None:
            if self.settings['folder'] is not None:
                self.dst_path = self.settings['folder']
                logging.debug("Using custom path: %s", self.dst_path)
        # Check destination exists
        if not os.path.exists(self.dst_path) and self.ptype is not None:
            self.push.failure("Folder for %s not found: %s"
                              % (self.ptype, self.dst_path))
        # Set up Query info
        action = self.filebot['action'].upper()
        # Object defaults
        self.query = {
            'file_types': r'(mkv|avi|m4v|mp4)',
            'skip': r'Skipped \[(.*)\] because \[(.*)\] already exists',
            'added_i': 1,
            'skip_i': 0,
            'reason': '%s already exists in %s' % (self.type, self.dst_path)
        }
        self.query['added'] = (r"\[%s\] Rename \[(.*)\] to \[(.*)\.%s\]"
                               % (action, self.query['file_types']))

    # ======== GET VIDEO ======== #

    def add(self, file_path):
        '''A new media file'''
        logging.info("Starting %s handler", self.type)
        # Set up query
        m_cmd = [self.filebot['bin'],
                 '-rename', file_path,
                 '--db', self.filebot['db'],
                 '--format', self.filebot['format'],
                 '--action', self.filebot['action'],
                 self.filebot['flags']]
        # Check for logfile
        if self.settings['log_file'] is not None:
            loginfo = [
                '--log', 'all',
                '--log-file', self.settings['log_file']]
            m_cmd.extend(loginfo)
        # If we are ignoring subs, remove all non-video files
        if self.settings['ignore_subs']:
            logging.debug("Ignoring subtitle files")
            self._remove_bad_files(file_path)
        # Get info
        return self.media_info(m_cmd, file_path)

    # ======== GET VIDEO INFO FROM FILEBOT ======== #

    def media_info(self, cmd, file_path):
        '''Get video info from filebot'''
        logging.info("Getting %s information", self.type)
        logging.debug("Query: %s", cmd)
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
        # Look for content
        added_data = findall(self.query['added'], output)
        skip_data = findall(self.query['skip'], output)
        # Check return
        results = []
        if len(added_data) > 0:
            for added_item in added_data:
                results.append(added_item[self.query['added_i']])
        # Get skipped results
        skipped = []
        if len(skip_data) > 0:
            for skip_item in skip_data:
                skipped.append(skip_item[self.query['skip_i']])
                logging.warning("File was skipped: %s (%s)",
                                skip_item[self.query['skip_i']],
                                self.query['reason'])
        # Return error if nothing found
        if len(skipped) == 0 and len(results) == 0:
            return self.match_error(file_path)
        # Return results
        return results, skipped

    # ======== REMOVE BAD FILES ======== #

    def _remove_bad_files(self, file_path):
        '''Removes non-video files from folder'''
        logging.info("Removing bad files")
        # Skip if this is not a folder
        if os.path.isfile(file_path):
            return
        # Look for bad files and remove them
        for item in os.listdir(file_path):
            regex = r'\.%s$' % self.query['file_types']
            if not search(regex, item):
                item_path = '%s/%s' % (file_path, item)
                os.unlink(item_path)
        return

    # ======== MATCH ERROR ======== #

    def match_error(self, name):
        '''Return a match error'''
        return self.push.failure("Unable to match %s: %s" % (self.type, name))
