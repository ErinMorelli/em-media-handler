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
'''Music media type module'''

# ======== IMPORT MODULES ======== #

import re
import logging
import mediahandler.types
from os import path, makedirs


# ======== MUSIC CLASS DECLARTION ======== #

class Tracks(mediahandler.types.Media):
    '''Tracks handler class'''

    # ======== SET GLOBAL CLASS OPTIONS ======== #

    def __init__(self, settings, push):
        '''Tracks class constuctor'''
        self.ptype = None
        super(Tracks, self).__init__(settings, push)
        # Beet
        self.beet = "/usr/local/bin/beet"
        self.beetslog = '%s/logs/beets.log' % path.expanduser("~")
        # Query
        self.tags = '-ql'
        self.query = r"(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n"
        # Check for single track
        if self.settings['single_track']:
            self.tags = "-sql"
            self.query = r"(Tagging track)\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"

    # ======== ADD MUSIC ======== #

    def add(self, file_path):
        '''Add music to beets library'''
        logging.info("Starting %s information handler", self.type)
        # Check for custom path in settings
        if self.settings['log_file'] is not None:
            self.beetslog = self.settings['log_file']
            logging.debug("Using custom beets log: %s", self.beetslog)
        # Check that log file path exists
        beetslog_dir = path.dirname(self.beetslog)
        if not path.exists(beetslog_dir):
            makedirs(beetslog_dir)
        # Set up query
        m_cmd = [self.beet,
                 "import", file_path,
                 self.tags, self.beetslog]
        # Get info
        return self.media_info(m_cmd, file_path)

    # ======== MUSIC OUTOUT PROCESSING ======== #

    def process_output(self, output, file_path):
        '''Tracks class output processor'''
        # Check for skips
        skipped = re.findall(r"(Skipping\.)\n", output)
        logging.info("Beets skipped %s items", len(skipped))
        # Extract Info
        music_find = re.compile(self.query)
        logging.debug("Search query: %s", self.query)
        # Format data
        music_data = music_find.findall(output)
        logging.info("Additions detected: %s", music_data)
        # Get results
        results = ''
        skips = False
        if len(music_data) > 0:
            for music_item in music_data:
                results = results + ("%s\n\t" % music_item[1])
        if len(skipped) > 0:
            skips = True
            results = results + ("\n%s items were skipped (see beets log)"
                                 % len(skipped))
        # Return error if nothing found
        if not skips and len(music_data) == 0:
            return self.match_error(file_path)
        # Return results
        return results, skips
