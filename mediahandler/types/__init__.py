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
Module: mediahandler.types

Module contains:

    - |MHMediaType|
        Parent class for all media type submodules. Includes the
        logic for the video media types (TV & movies).

Media Type Submodules:

    - |mediahandler.types.audiobooks|

    - |mediahandler.types.movies|

    - |mediahandler.types.music|

    - |mediahandler.types.tv|

'''

import os
import logging
from re import findall, search, sub
from subprocess import Popen, PIPE

import mediahandler as mh


class MHMediaType(mh.MHObject):
    '''Parent class for the media type submodule classes.

    Required arguments:
        - settings
            Dict or MHSettings object.

        - push
            MHPush object.

    Public method:
        - |add()|
            Main wrapper function for adding media files. Processes
            calls to Beets and Filebot.
    '''

    def __init__(self, settings, push):
        '''Initialize the MHMediaType class.

        Required arguments:
            - settings
                Dict or MHSettings object.

            - push
                MHPush object.
        '''

        super(MHMediaType, self).__init__(settings, push)

        # Set up class members
        self.push = push
        self.dst_path = ''
        self.type = sub(r'^mh', '', type(self).__name__.lower())

        # If the subclass didn't define a ptype, set default
        if not hasattr(self, 'ptype'):
            self.ptype = 'Media Type'

        # Type specific
        if self.ptype is not None:

            # Set destination path
            self.dst_path = os.path.join(
                os.path.expanduser("~"), 'Media', self.ptype)

            # Check for custom path in settings
            if hasattr(self, 'folder'):
                if self.folder is not None:
                    self.dst_path = self.folder
                    logging.debug("Using custom path: %s", self.dst_path)

            # Check destination exists
            if not os.path.exists(self.dst_path):
                self.push.failure("Folder for {0} not found: {1}".format(
                    self.ptype, self.dst_path))

    def _video_settings(self):
        '''Set MHMediaType object methods for video types.

        Sets up Filebot query values and post-query regex processing values.
        '''

        # Check for filebot
        if not self.filebot:
            self.push.failure(
                "Filebot required to process {0} files".format(self.ptype))

        # Filebot
        cmd_info = self.MHSettings({
            'action': 'copy',
            'db': '',
            'format': os.path.join(self.dst_path, self.format),
            'flags': ['-r', '-non-strict']
        })
        self.__dict__.update({'cmd': cmd_info})

        # Object defaults
        query = self.MHSettings({
            'file_types': r'(mkv|avi|m4v|mp4)',
            'skip': r'Skipped \[(.*)\] because \[(.*)\] already exists',
            'added_i': 1,
            'skip_i': 0,
            'reason': '{0} already exists in {1}'.format(
                self.type, self.dst_path)
        })
        query.added = r'\[{0}\] Rename \[(.*)\] to \[(.*)\.{1}\]'.format(
            self.cmd.action.upper(), query.file_types)
        self.__dict__.update({'query': query})

        return

    def add(self, file_path):
        '''Wrapper for Filebot requests.

        Sets up Filebot CLI query using object member values.
        '''

        logging.info("Starting %s handler", self.type)

        # Set up query
        m_cmd = [self.filebot,
                 '-rename', file_path,
                 '--db', self.cmd.db,
                 '--format', self.cmd.format,
                 '--action', self.cmd.action]
        m_cmd.extend(self.cmd.flags)

        # Check for logfile
        if self.log_file is not None:
            loginfo = [
                '--log', 'all',
                '--log-file', self.log_file]
            m_cmd.extend(loginfo)

        # If ignoring subtitles, remove all non-video files
        if self.ignore_subs:
            logging.debug("Ignoring subtitle files")
            self._remove_bad_files(file_path)

        return self._media_info(m_cmd, file_path)

    def _media_info(self, cmd, file_path):
        '''Makes request to Beets and Filebot.

        Sends results to _process_output().
        '''

        logging.debug("Query: %s", cmd)

        # Process query
        query = Popen(cmd, stdout=PIPE)

        # Get output
        (output, err) = query.communicate()
        logging.debug("Query output: %s", output)
        logging.debug("Query return errors: %s", err)

        return self._process_output(output, file_path)

    def _process_output(self, output, file_path):
        '''Parses response from _media_info() query.

        Returns good results and any skipped files.
        '''

        logging.info("Processing query output")

        # Look for content
        added_data = findall(self.query.added, output)
        skip_data = findall(self.query.skip, output)

        # Check return
        results = []
        if len(added_data) > 0:
            for added_item in added_data:
                results.append(added_item[self.query.added_i])

        # Get skipped results
        skipped = []
        if len(skip_data) > 0:
            for skip_item in skip_data:
                skipped.append(skip_item[self.query.skip_i])
                logging.warning("File was skipped: %s (%s)",
                                skip_item[self.query.skip_i],
                                self.query.reason)

        # Return error if nothing found
        if len(skipped) == 0 and len(results) == 0:
            return self._match_error(file_path)

        return results, skipped

    def _remove_bad_files(self, file_path):
        '''Removes non-video files from media folder.

        Only used when 'ignore_subs' setting is True.
        '''

        logging.info("Removing bad files")
        # Skip if this is not a folder
        if os.path.isfile(file_path):
            return

        # Look for bad files and remove them
        regex = r'\.{0}$'.format(self.query.file_types)
        for item in os.listdir(file_path):

            item_path = os.path.join(file_path, item)

            # If it's a folder, iterate again
            if os.path.isdir(item_path):
                self._remove_bad_files(item_path)

            # Otherwise check for non-video files
            elif not search(regex, item):
                os.unlink(item_path)

        return

    def _match_error(self, name):
        '''Returns a match error via the MHPush object.
        '''
        return self.push.failure(
            "Unable to match {0} files: {1}".format(self.type, name))
