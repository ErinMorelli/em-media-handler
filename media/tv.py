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
		self.tvPath = 'Television'


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


	def episodeHandler(self):
		logging.info("Starting episode information handler")
		# Set Variables
		tvFormat = "%s/{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}" % self.tvPath
		tvDB = "thetvdb"
		# Get info
		new_file = self.__getInfo(tvFormat, tvDB)
		logging.debug("New file: %s", new_file)
		# Check for failure
		if new_file == None:
			return None
		# Set search query
		ePath = re.escape(self.tvPath)
		tvFind = "%s\/(.*)\/(.*)\/.*\.S\d{2,4}E(\d{2,3}).\w{3}" % ePath
		logging.debug("Search query: %s", tvFind)
		# Extract info
		episode = re.search(tvFind, new_file)
		if episode == None:
			return None
		# Show title
		show_name = episode.group(1)
		# Season 
		season = episode.group(2)
		# Episode 
		ep_num = episode.group(3)
		ep_num_fix = re.sub('^0', '', ep_num)
		episode = "Episode %s" % ep_num_fix
		# Set title
		ep_title = "%s (%s, %s)" % (show_name, season, episode)
		# Return Show Name, Season, Episode (file)
		return ep_title, new_file
