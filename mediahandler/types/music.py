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
'''Music media type module'''

# ======== IMPORT MODULES ======== #

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
        self.beet = path.join('/', 'usr', 'local', 'bin', 'beet')
        self.beetslog = path.join(path.expanduser("~"), 'logs', 'beets.log')
        # Query info
        self.query = {
            'tags': '-ql',
            'added': r"(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n",
            'skip': r"(^|\n).*\/(.*) \(\d+ items\)\nSkipping.\n",
            'added_i': 1,
            'skip_i': 1,
            'reason': "see beets log",
        }
        # Check for single track
        if self.settings['single_track']:
            self.query['tags'] = "-sql"
            single_regex = r"(Tagging track)\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"
            self.query['added'] = single_regex

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
                 self.query['tags'], self.beetslog]
        # Get info
        return self.media_info(m_cmd, file_path)
