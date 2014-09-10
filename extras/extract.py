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

class Extract:
	def __init__(self, filename):
		logging.info("Initializing extraction class")
		self.file = filename
		self.filebot = "/usr/bin/filebot"


	def fileHandler(self):
		logging.info("Getting files from compressed folder")
		# Set up query
		mCMD = [self.filebot, 
			"-extract", self.file
		]
		logging.debug("Query: %s", mCMD)
		# Process query
		p = Popen(mCMD, stdout=PIPE)
		# Get output
		(output, err) = p.communicate()
		logging.debug("Query output: %s", output)
		logging.debug("Query return errors: %s", err)
		# Process output
		fileinfo = re.search(r"Extracting files \[(.*)\]\n", output)
		if fileinfo == None:
			return None
		extracted = fileinfo.group(1)
		# Break into array
		new_files = extracted.split(", ")
		# Return array of extracted files
		return new_files
