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

import ConfigParser
import imp, os, logging


# ======== LOOK FOR MODULE ======== #

def __findModule(parentMod, subMod):
	try:
		modInfo = imp.find_module(parentMod)
		mod = imp.load_module(parentMod, *modInfo)
		imp.find_module(subMod, mod.__path__) # __path__ is already a list
		return True
	except ImportError:
		errMsg = 'Module %s.%s is not installed' % (parentMod,subMod)
		raise ImportError(errMsg)


# ======== LOGGING ======== #

def __initLogging(settings):
	# Set defaults
	logFile = '~/log/mediaHandler.log'
	logLevel = 40
	# Look for exceptions
	if settings['General']['logfile'] != None:
		logFile = settings['General']['logfile']
	if settings['General']['loglevel'] != None:
		logLevel =  int(settings['General']['loglevel'])
	# Config logging
	logging.basicConfig(
		filename=logFile,
		format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
		level=logLevel,
	)
	# Enable deluge logging
	if settings['General']['deluge']:
		from deluge.log import setupLogger
		setupLogger()
	return


# ======== CHECK MODULES ======== #

def __checkModules(settings):
	# Check for logging
	if settings['General']['logging']:
		__initLogging(settings)
		logging.info('Logging enabled')
	# Check deluge requirements
	if settings['General']['deluge']:
		# Check for Twisted
		if __findModule('twisted', 'internet'):
			logging.debug('Twisted.internet module found')
		# Check for Deluge
		if __findModule('deluge', 'ui') and __findModule('deluge', 'log'):
			logging.debug('Deluge modules found')
	# Check video requirements
	if settings['TV']['enabled'] or settings['Movies']['enabled']:
		# Check for Filebot
		if os.path.isfile('/usr/bin/filebot'):
			logging.debug('Filebot application found')
	# Check music requirements
	if settings['Music']['enabled']:
		# Check for Beets
		if __findModule('beets', 'util'):
			logging.debug('Beets.util module found')
	# Check audiobook requirements
	if settings['Audiobooks']['enabled']:
		# Check for Google API
		if __findModule('apiclient', 'discovery'):
			logging.debug('Apiclient.discovery module found')
		# Is chaptering enabled
		if settings['Audiobooks']['makechapters']:
			# Check for Mutagen
			if __findModule('mutagen', 'mp3') and __findModule('mutagen', 'ogg'):
				logging.debug('Mutagen modules found')
			# Check fo ABC
			if os.path.isfile('/usr/bin/abc.php'):
				logging.debug('ABC applciation found')
	return


# ======== PARSE CONFIG FILE ======== #

def getConfig(configFile):
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
			except:
				newOptions[option] = None
		# Populate hash
		settings[section] = newOptions
	# Make bools
	settings['General']['deluge'] = Config.getboolean('General', 'deluge')
	settings['General']['logging'] = Config.getboolean('General', 'logging')
	settings['General']['keepfiles'] = Config.getboolean('General', 'keepFiles')
	settings['Audiobooks']['makechapters'] = Config.getboolean('Audiobooks', 'makeChapters')
	# Check that appropriate modules are installed
	__checkModules(settings)
	# Return setting hash
	return settings
