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
	logFile = '%s/logs/mediaHandler.log' % os.path.expanduser("~")
	logLevel = 40
	# Look for exceptions
	if settings['General']['log_file'] != None:
		logFile = settings['General']['log_file']
	if settings['General']['log_level'] != None:
		logLevel =  int(settings['General']['log_level'])
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
		__findModule('twisted', 'internet')
		# Check for Deluge
		__findModule('deluge', 'ui')
		__findModule('deluge', 'log')
	# Check video requirements
	if settings['TV']['enabled'] or settings['Movies']['enabled']:
		# Check for Filebot
		if not os.path.isfile('/usr/bin/filebot'):
			raise ImportError('Filebot application not found')
	# Check music requirements
	if settings['Music']['enabled']:
		# Check for Beets
		__findModule('beets', 'util')
	# Check audiobook requirements
	if settings['Audiobooks']['enabled']:
		# Check for Google API
		__findModule('apiclient', 'discovery')
		# Is chaptering enabled
		if settings['Audiobooks']['make_chapters']:
			# Check for Mutagen
			__findModule('mutagen', 'mp3')
			__findModule('mutagen', 'ogg')
			# Check fo ABC
			if not os.path.isfile('/usr/bin/abc.php'):
				raise ImportError('ABC applciation not found')
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
	settings['General']['keep_files'] = Config.getboolean('General', 'keep_files')
	settings['Audiobooks']['make_chapters'] = Config.getboolean('Audiobooks', 'make_chapters')
	# Check that appropriate modules are installed
	__checkModules(settings)
	# Return setting hash
	return settings
