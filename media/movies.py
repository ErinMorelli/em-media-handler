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

from subprocess import Popen, PIPE
import re, logging


# ======== CLASS DECLARTION ======== #

class Rename:
	def __init__(self, filepath):
		logging.info("Initializing renaming class")
		# The File
		self.file = filepath
		# Filebot Options
		self.filebot = "/usr/bin/filebot"
		self.action = "COPY"
		self.strict = "-non-strict"
		self.analytics = "-no-analytics"
		# Local paths
		self.movPath = 'Movies'


	def __getInfo(self, mFormat, mDB):
		logging.info("Getting episode information")
		# Set up query
		mCMD = [self.filebot, 
			"-rename", self.file, 
			"--db", mDB, 
			"--format", mFormat,
			"--action", self.action.lower(),
			self.strict, self.analytics
		]
		logging.debug("Query: %s", mCMD)
		# Process query
		p = Popen(mCMD, stdout=PIPE)
		# Get output
		(output, err) = p.communicate()
		logging.debug("Query output: %s", output)
		logging.debug("Query return errors: %s", err)
		# Process output
		query = "\[%s\] Rename \[.*\] to \[(.*)\]" % self.action
		fileinfo = re.search(query, output)
		if fileinfo == None:
			return None
		new_file = fileinfo.group(1)
		# Return new file
		return new_file


	def movieHandler(self):
		logging.info("Starting movie information handler")
		# Set Variables
		movFormat = "%s/{n} ({y})" % self.movPath
		movDB = "themoviedb"
		# Get info
		new_file = self.__getInfo(movFormat, movDB)
		logging.debug("New file: %s", new_file)
		# Check for failure
		if new_file == None:
			return None
		# Set search query
		ePath = re.escape(self.movPath)
		movFind = "%s\/(.*\(\d{4}\))\.\w{3}" % ePath
		logging.debug("Search query: %s", movFind)
		# Extract info
		movie = re.search(movFind, new_file)
		if movie == None:
			return None
		# Set title
		mov_title = movie.group(1)
		# Return Movie Title
		return mov_title, new_file

