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

import logging
from os import path
from media import getInfo
from re import escape, search, sub


# ======== CLASS DECLARTION ======== #

class Episode:

    # ======== INIT EPISODE CLASS ======== #

    def __init__(self, settings):
        logging.info("Initializing episode renaming class")
        # Default TV path
        self.tvPath = '%s/Media/Television' % path.expanduser("~")
        # Check for custom path in settings
        if 'folder' in settings.keys():
            if path.exists(settings['folder']):
                self.tvPath = settings['folder']
                logging.debug("Using custom path: %s" % self.tvPath)

    # ======== GET EPISODE ======== #

    def getEpisode(self, filePath):
        logging.info("Starting episode information handler")
        # Set Variables
        tvForm = ("%s/{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
                  % self.tvPath)
        tvDB = "thetvdb"
        # Get info
        newFile = getInfo(tvForm, tvDB, filePath)
        logging.debug("New file: %s", newFile)
        # Check for failure
        if newFile is None:
            return None
        # Set search query
        ePath = escape(self.tvPath)
        tvFind = "%s\/(.*)\/(.*)\/.*\.S\d{2,4}E(\d{2,3}).\w{3}" % ePath
        logging.debug("Search query: %s", tvFind)
        # Extract info
        episode = search(tvFind, newFile)
        if episode is None:
            return None
        # Show title
        showName = episode.group(1)
        # Season
        season = episode.group(2)
        # Episode
        epNum = episode.group(3)
        epNumFix = sub('^0', '', epNum)
        episode = "Episode %s" % epNumFix
        # Set title
        epTitle = "%s (%s, %s)" % (showName, season, episode)
        # Return Show Name, Season, Episode (file)
        return epTitle, newFile
