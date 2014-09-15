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

import imp
import logging
from os import path, access, R_OK
from ConfigParser import ConfigParser


# ======== LOOK FOR MODULE ======== #

def __findModule(parentMod, subMod):
    try:
        modInfo = imp.find_module(parentMod)
        mod = imp.load_module(parentMod, *modInfo)
        imp.find_module(subMod, mod.__path__)
        return True
    except ImportError:
        errMsg = 'Module %s.%s is not installed' % (parentMod, subMod)
        raise ImportError(errMsg)


# ======== LOGGING ======== #

def __initLogging(settings):
    # Set defaults
    logFile = '%s/logs/mediaHandler.log' % path.expanduser("~")
    logLevel = 40
    # Look for exceptions
    if settings['Logging']['file_path'] is not None:
        logFile = settings['Logging']['file_path']
    if settings['Logging']['level'] is not None:
        logLevel = int(settings['Logging']['level'])
    # Config logging
    logging.basicConfig(
        filename=logFile,
        format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
        level=logLevel,
    )
    # Enable deluge logging
    if settings['Deluge']['enabled']:
        from deluge.log import setupLogger
        setupLogger()
    return


# ======== CHECK MODULES ======== #

def __checkModules(settings):
    # Check for logging
    if settings['Logging']['enabled']:
        __initLogging(settings)
        logging.info('Logging enabled')
    # Check deluge requirements
    if settings['Deluge']['enabled']:
        # Check for Twisted
        __findModule('twisted', 'internet')
        # Check for Deluge
        __findModule('deluge', 'ui')
        __findModule('deluge', 'log')
    # Check video requirements
    if settings['TV']['enabled'] or settings['Movies']['enabled']:
        # Check for Filebot
        if not path.isfile('/usr/bin/filebot'):
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
            if not path.isfile('/usr/bin/abc.php'):
                raise ImportError('ABC application not found')
    return


# ======== PARSE CONFIG FILE ======== #

def getConfig(configFile):
    # Bool options
    __boolOptions = ["enabled",
                     "keep_files",
                     "make_chapters"]
    # Read config file
    Config = ConfigParser()
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
                if option in __boolOptions:
                    newOptions[option] = Config.getboolean(section, option)
                else:
                    newOptions[option] = Config.get(section, option)
            except:
                newOptions[option] = None
        # Populate hash
        settings[section] = newOptions
    # Check that appropriate modules are installed
    __checkModules(settings)
    # Return setting hash
    return settings


# ======== MAKE CONFIG FILE ======== #

def makeConfig(newPath):
    # Set default path
    configPath = ('%s/.config/mediaHandler/mediaHandler.conf' %
                  path.expanduser("~"))
    # Check for user-provided path
    if newPath is not None:
        configPath = newPath
    # Check that config exists
    if path.isfile(configPath):
        # Check config file permissions
        if not access(configPath, R_OK):
            raise Warning('Configuration file cannot be opened')
    else:
        config = ConfigParser()
        # General section defaults
        config.add_section('General')
        config.set('General', 'keep_files', 'true')
        # Deluge section defaults
        config.add_section('Deluge')
        config.set('Deluge', 'enabled', 'true')
        config.set('Deluge', 'host', '127.0.0.1')
        config.set('Deluge', 'port', '58846')
        config.set('Deluge', 'user', '')
        config.set('Deluge', 'pass', '')
        # Deluge section defaults
        config.add_section('Logging')
        config.set('Logging', 'enabled', 'false')
        config.set('Logging', 'level', '')
        config.set('Logging', 'file_path', '')
        # Pushover section defaults
        config.add_section('Pushover')
        config.set('Pushover', 'enabled', 'false')
        config.set('Pushover', 'api_key', '')
        config.set('Pushover', 'user_key', '')
        config.set('Pushover', 'notify_name', '')
        # TV section defaults
        config.add_section('TV')
        config.set('TV', 'enabled', 'true')
        config.set('TV', 'folder', '')
        # Movies section defaults
        config.add_section('Movies')
        config.set('Movies', 'enabled', 'true')
        config.set('Movies', 'folder', '')
        config.set('Movies', 'log_file', '')
        # Music section defaults
        config.add_section('Music')
        config.set('Music', 'enabled', 'false')
        # Audiobooks section defaults
        config.add_section('Audiobooks')
        config.set('Audiobooks', 'enabled', 'false')
        config.set('Audiobooks', 'folder', '')
        config.set('Audiobooks', 'api_key', '')
        config.set('Audiobooks', 'make_chapters', 'false')
        config.set('Audiobooks', 'chapter_length', '8')
        # Writing our configuration file to 'example.cfg'
        with open(configPath, 'wb') as configFile:
            config.write(configFile)
    # Return with path to file
    return configPath
