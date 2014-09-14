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

import re, os, logging, media


# ======== CLASS DECLARTION ======== #

class Movie:

	def __init__(self, settings):
		logging.info("Initializing renaming class")
		# Default TV path
		self.movPath = '%s/Media/Movies' % os.path.expanduser("~")
		# Check for custom path in settings
		if 'folder' in settings.keys():
			if os.path.exists(settings['folder']):
				self.movPath = settings['folder']
				logging.debug("Using custom path: %s" % self.tvPath)


	def getMovie(self, filePath):
		logging.info("Starting movie information handler")
		# Set Variables
		movFormat = "%s/{n} ({y})" % self.movPath
		movDB = "themoviedb"
		# Get info
		newFile = media.getInfo(movFormat, movDB, filePath)
		logging.debug("New file: %s", newFile)
		# Check for failure
		if newFile == None:
			return None
		# Set search query
		ePath = re.escape(self.movPath)
		movFind = "%s\/(.*\(\d{4}\))\.\w{3}" % ePath
		logging.debug("Search query: %s", movFind)
		# Extract info
		movie = re.search(movFind, newFile)
		if movie == None:
			return None
		# Set title
		movTitle = movie.group(1)
		# Return Movie Title
		return movTitle, newFile

