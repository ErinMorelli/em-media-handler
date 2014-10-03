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
'''Configuration file handler'''


# ======== IMPORT MODULES ======== #

import imp
import logging
from os import path, makedirs, access, R_OK

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


# ======== LOOK FOR MODULE ======== #

def __find_module(parent_mod, sub_mod):
    '''Look to see if module is installed'''
    try:
        mod_info = imp.find_module(parent_mod)
        mod = imp.load_module(parent_mod, *mod_info)
        imp.find_module(sub_mod, mod.__path__)
        return True
    except ImportError:
        err_msg = 'Module %s.%s is not installed' % (parent_mod, sub_mod)
        raise ImportError(err_msg)


# ======== LOGGING ======== #

def __init_logging(settings):
    '''Turn on logging'''
    # Set defaults
    log_file = '%s/logs/mediaHandler.log' % path.expanduser("~")
    log_level = 40
    # Look for exceptions
    if settings['Logging']['file_path'] is not None:
        log_file = settings['Logging']['file_path']
    if settings['Logging']['level'] is not None:
        log_level = int(settings['Logging']['level'])
    # Make sure log file dir exists
    log_path = path.dirname(log_file)
    if not path.exists(log_path):
        makedirs(log_path)
    # Config logging
    logging.basicConfig(
        filename=log_file,
        format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
        level=log_level,
    )
    # Enable deluge logging
    if settings['Deluge']['enabled']:
        from deluge.log import setupLogger
        setupLogger()
    return


# ======== CHECK MODULES ======== #

def __check_modules(settings):
    '''Check that needed modules are installed'''
    # Check for logging
    if settings['Logging']['enabled']:
        __init_logging(settings)
        logging.info('Logging enabled')
    # Check deluge requirements
    if settings['Deluge']['enabled']:
        # Check for Twisted
        __find_module('twisted', 'internet')
        # Check for Deluge
        __find_module('deluge', 'ui')
        __find_module('deluge', 'log')
    # Check video requirements
    if settings['TV']['enabled'] or settings['Movies']['enabled']:
        # Check for Filebot
        if (not path.isfile('/usr/bin/filebot') and
           not path.isfile('/usr/local/bin/filebot')):
            raise ImportError('Filebot application not found')
    # Check music requirements
    if settings['Music']['enabled']:
        # Check for Beets
        __find_module('beets', 'util')
    # Check audiobook requirements
    if settings['Audiobooks']['enabled']:
        # Check for Google API
        __find_module('apiclient', 'discovery')
        # Is chaptering enabled
        if settings['Audiobooks']['make_chapters']:
            # Check for Mutagen
            __find_module('mutagen', 'mp3')
            __find_module('mutagen', 'ogg')
            # Check fo ABC
            if not path.isfile('/usr/bin/abc.php'):
                raise ImportError('ABC application not found')
    return


# ======== PARSE CONFIG FILE ======== #

def getconfig(config_file):
    '''Read config file'''
    # Bool options
    __bool_options = ["enabled",
                      "keep_files",
                      "make_chapters"]
    # Read config file
    config = ConfigParser()
    config.read(config_file)
    # Loop through sections
    settings = {}
    sections = config.sections()
    for section in sections:
        # Loop through options
        new_options = {}
        options = config.options(section)
        for option in options:
            new_options[option] = None
            if option in __bool_options:
                new_options[option] = config.getboolean(section, option)
            else:
                new_options[option] = config.get(section, option)
        # Populate hash
        settings[section] = new_options
    # Check that appropriate modules are installed
    __check_modules(settings)
    # Return setting hash
    return settings


# ======== MAKE CONFIG FILE ======== #

def makeconfig(new_file):
    '''Generate default config file'''
    # Set default path
    config_file = ('%s/.config/mediahandler/settings.conf' %
                   path.expanduser("~"))
    # Check for user-provided path
    if new_file is not None:
        config_file = new_file
    # Check that config exists
    if path.isfile(config_file):
        # Check config file permissions
        if not access(config_file, R_OK):
            raise Warning('Configuration file cannot be opened')
    else:
        config = ConfigParser()
        # General section defaults
        config.add_section('General')
        config.set('General', 'keep_files', 'true')
        # Deluge section defaults
        config.add_section('Deluge')
        config.set('Deluge', 'enabled', 'false')
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
        # Music section defaults
        config.add_section('Music')
        config.set('Music', 'enabled', 'false')
        config.set('Music', 'log_file', '')
        # Audiobooks section defaults
        config.add_section('Audiobooks')
        config.set('Audiobooks', 'enabled', 'false')
        config.set('Audiobooks', 'folder', '')
        config.set('Audiobooks', 'api_key', '')
        config.set('Audiobooks', 'make_chapters', 'false')
        config.set('Audiobooks', 'chapter_length', '8')
        # Make directories for config file
        config_path = path.dirname(config_file)
        if not path.exists(config_path):
            makedirs(config_path)
        # Write new configuration file to path
        with open(config_file, 'w') as config_file_open:
            config.write(config_file_open)
    # Return with path to file
    return config_file
