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
		# Beet Options
		self.beet = "/usr/local/bin/beet"
		self.beetslog = "beetslog.log"


	def musicHandler(self, isSingle=False):
		logging.info("Starting music information handler")
		# Set Variables
		if isSingle:
			mType = "Song"
			mTags = "-sql"
			mQuery = "Tagging track\:\s(.*)\nURL\:\n\s{1,4}(.*)\n\((Similarity\: .*%)\)"
		else:
			mType = "Album"
			mTags = "-ql"
			mQuery = "(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n\((Similarity\: .*%)\)"
		# Set up query
		mCMD = [self.beet,
			"import", self.file,
			mTags, self.beetslog,
		]
		logging.debug("Query: %s", mCMD)
		# Process query
		p = Popen(mCMD, stdout=PIPE, stderr=PIPE)
		# Get output
		(output, err) = p.communicate()
		logging.debug("Query output: %s", output)
		logging.debug("Query return errors: %s", err)
		# Process output
		if err != '':
			return True, err
		# Extract Info 
		musicFind = re.compile(mQuery)
		logging.debug("Search query: %s", mQuery)
		# Format data
		musicData = musicFind.search(output)
		musicInfo = "%s: %s" % (mType, musicData.group(2))
		logging.info("MusicBrainz URL: %s" % musicData.group(3))
		logging.info(musicData.group(4))
		# Return music data
		return False, musicInfo
