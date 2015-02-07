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
Module: mediahandler.types.music

Module contains:

    - |MHMusic|
        Child class of MHMediaType for the music media type.

'''

import logging
import mediahandler.types
from os import path, makedirs


class MHMusic(mediahandler.types.MHMediaType):
    '''Child class of MHMediaType for the music media type.

    Required arguments:
        - settings
            Dict or MHSettings object.
        - push
            MHPush object.

    Public method:
        - |add()|
            inherited from parent MHMediaType.
    '''

    def __init__(self, settings, push):
        '''Initialize the MHMusic class.

        Required arguments:
            - settings
                Dict or MHSettings object.
            - push
                MHPush object.
        '''

        # Set ptype and call super
        self.ptype = None
        super(MHMusic, self).__init__(settings, push)

        # Set beets log file path
        self.beetslog = path.join(path.expanduser("~"), 'logs', 'beets.log')

        # Set regex query info
        self.query = self.MHSettings({
            'tags': '-ql',
            'added': r"(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n",
            'skip': r"(^|\n).*\/(.*) \(\d+ items\)\nSkipping.\n",
            'added_i': 1,
            'skip_i': 1,
            'reason': "see beets log",
        })

        # Check for single track
        if self.single_track:
            self.query.tags = "-sql"
            single_regex = r"(Tagging track)\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"
            self.query.added = single_regex

    def add(self, file_path):
        '''Overrides the MHMediaType object to process Beets requests.

        Sets up Beets CLI query using object member values.
        '''

        logging.info("Starting %s information handler", self.type)

        # Check for custom path in settings
        if self.log_file is not None:
            self.beetslog = self.log_file
            logging.debug("Using custom beets log: %s", self.beetslog)

        # Check that log file path exists
        beetslog_dir = path.dirname(self.beetslog)
        if not path.exists(beetslog_dir):
            makedirs(beetslog_dir)

        # Set up query
        m_cmd = [self.beets,
                 "import", file_path,
                 self.query.tags, self.beetslog]

        return self._media_info(m_cmd, file_path)
