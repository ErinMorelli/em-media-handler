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

import ConfigParser, pkgutil, imp

from twisted.internet import reactor
#from deluge.ui.client import client
#from deluge.log import setupLogger


def __getConfig(configFile):
	# Read config file
	Config = ConfigParser.ConfigParser()
	Config.read(configFile)
	# Loop through sections
	settings = {}
	sections = Config.sections()
	for section in sections:
		# Loop through options
		newOptions = {}
		options = Config.options(section)
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
		# Populate hash
		settings[section] = newOptions
	# Make bools
	settings['General']['deluge'] = Config.getboolean('General', 'deluge')
	settings['General']['logging'] = Config.getboolean('General', 'logging')
	settings['General']['keepFiles'] = Config.getboolean('General', 'keepFiles')
	settings['Audiobooks']['makeChapters'] = Config.getboolean('Audiobooks', 'makeChapters')
	# Return setting hash
	return settings


def __findModule(parentMod, subMod):
	try:
		modInfo = imp.find_module(parentMod)
		mod = imp.load_module(parentMod, *modInfo)
		imp.find_module(subMod, mod.__path__) # __path__ is already a list
		return True
	except ImportError:
		return False


def __checkModules(settings):
	# Check required modules
	if settings['General']['deluge']:
		print 'deluge'
		# Check for Twisted
		if __findModule('twisted', 'internet'):
			print "FOUND: twisted"
		# Check for Deluge
		if __findModule('deluge', 'ui') and __findModule('deluge', 'log'):
			print "FOUND: deluge"

	if settings['TV']['enabled'] or settings['Movies']['enabled']:
		print 'filebot'
		# Check for Filebot

	if settings['Music']['enabled']:
		print 'beets'
		# check for Beets
		if __findModule('beets', 'util'):
			print "FOUND: beets"

	if settings['Audiobooks']['enabled']:
		print 'books'
		# check for google api
		if __findModule('apiclient', 'discovery'):
			print "FOUND: apiclient"

		if settings['Audiobooks']['makeChapters']:
			# check for abc, mutagen
			print 'chapters'
			if __findModule('mutagen', 'mp3') and __findModule('mutagen', 'ogg'):
				print "FOUND: mutagen"
	return


# If this is commandline, get args & run
if __name__=='__main__':
	settings = __getConfig('mediaHandler.conf')
	__checkModules(settings)
