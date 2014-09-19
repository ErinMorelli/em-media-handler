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


# ======== IMPORT MODULES ======== #

import re
import logging
from os import path, makedirs
from subprocess import Popen, PIPE


# ======== CLASS DECLARTION ======== #

class newMusic:

    # ======== INIT MUSIC CLASS ======== #

    def __init__(self, settings):
        logging.info("Initializing renaming class")
        # Beet Options
        self.beet = "/usr/local/bin/beet"
        self.beetslog = '%s/logs/beets.log' % path.expanduser("~")
        # Check for custom path in settings
        if settings['log_file'] != '':
            self.beetslog = settings['log_file']
            logging.debug("Using custom beets log: %s" % self.beetslog)
        # Check that log file path exists
        beetslogDir = path.dirname(self.beetslog)
        if not path.exists(beetslogDir):
            makedirs(beetslogDir)

    # ======== ADD MUSIC ======== #

    def addMusic(self, filePath, isSingle=False):
        logging.info("Starting music information handler")
        # Set Variables
        if isSingle:
            mType = "Song"
            mTags = "-sql"
            mQuery = "Tagging track\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"
        else:
            mType = "Album"
            mTags = "-ql"
            mQuery = "(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n"
        # Set up query
        mCMD = [self.beet,
                "import", filePath,
                mTags, self.beetslog]
        logging.debug("Query: %s", mCMD)
        # Process query
        p = Popen(mCMD, stdout=PIPE, stderr=PIPE)
        # Get output
        (output, err) = p.communicate()
        logging.debug("Query output: %s", output)
        logging.debug("Query return errors: %s", err)
        # Process output
        if err != '':
            return None
        # Check for skip
        if re.search(r"(Skipping\.)\n", output):
            logging.warning("Beets is skipping the import: %s" % output)
            return None
        # Extract Info
        musicFind = re.compile(mQuery)
        logging.debug("Search query: %s", mQuery)
        # Format data
        musicData = musicFind.search(output)
        musicInfo = "%s: %s" % (mType, musicData.group(2))
        logging.info("MusicBrainz URL: %s" % musicData.group(3))
        # Return music data
        return musicInfo
