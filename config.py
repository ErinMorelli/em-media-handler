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

import ConfigParser, pkgutil




Config = ConfigParser.ConfigParser()
Config.read('mediaHandler.conf')


settings = {}
sections = Config.sections()
for section in sections:
	options = Config.options(section)
	newOptions = {}
	for option in options:
		try:
			if option == "enabled":
				newOptions[option] = Config.getboolean(section, option)
			else:
				newOptions[option] = Config.get(section, option)
			if newOptions[option] == -1:
				print "skip: %s" % option

		except:
			print "exception on %s!" % option
			newOptions[option] = None
	settings[section] = newOptions

# Make bools
settings['General']['deluge'] = Config.getboolean('General', 'deluge')
settings['General']['logging'] = Config.getboolean('General', 'logging')
settings['General']['keepFiles'] = Config.getboolean('General', 'keepFiles')
settings['Audiobooks']['makeChapters'] = Config.getboolean('Audiobooks', 'makeChapters')


# Check required modules
if settings['General']['deluge']:
	# check for deluge, twisted
	print 'deluge'

if settings['TV']['enabled'] or settings['Movies']['enabled']:
	# check for filebot
	print 'tv or movie'

if settings['Music']['enabled']:
	# check for beets
	print 'music'

if settings['Audiobooks']['enabled']:
	# check for google api
	print 'books'
	if settings['Audiobooks']['makeChapters']:
		# check for abc, mutagen
		print 'chapters'



'''
try:
    imp.find_module('eggs')
    found = True
except ImportError:
    found = False

twisted.internet, deluge.ui.client, deluge.log, apiclient.discovery, mutagen.mp3, mutagen.ogg
'''