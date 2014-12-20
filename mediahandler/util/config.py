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

import os
import imp
import logging
import mediahandler.util as util

try:
    import ConfigParser as CP
except ImportError:
    import configparser as CP


# ======== SET GLOBALS ======== #

PARSER = CP.ConfigParser()
STRUCT = [
    {
        'section': 'General',
        'options': [
            ['keep_files', 'bool', 'true'],
            ['keep_if_duplicates', 'bool', 'true'],
        ]
    },
    {
        'section': 'Deluge',
        'options': [
            ['enabled', 'bool', 'false'],
            ['host', 'string', '127.0.0.1'],
            ['port', 'number', '58846'],
            ['user', 'string', ''],
            ['pass', 'string', ''],
        ]
    },
    {
        'section': 'Logging',
        'options': [
            ['enabled', 'bool', 'false'],
            ['level', 'number', ''],
            ['log_file', 'file', ''],
        ]
    },
    {
        'section': 'Pushover',
        'options': [
            ['enabled', 'bool', 'false'],
            ['api_key', 'string', ''],
            ['user_key', 'string', ''],
            ['notify_name', 'string', ''],
        ]
    },
    {
        'section': 'TV',
        'options': [
            ['enabled', 'bool', 'true'],
            ['folder', 'folder', ''],
        ]
    },
    {
        'section': 'Movies',
        'options': [
            ['enabled', 'bool', 'true'],
            ['folder', 'folder', ''],
        ]
    },
    {
        'section': 'Music',
        'options': [
            ['enabled', 'bool', 'false'],
            ['log_file', 'file', ''],
        ]
    },
    {
        'section': 'Audiobooks',
        'options': [
            ['enabled', 'bool', 'false'],
            ['folder', 'folder', ''],
            ['api_key', 'string', ''],
            ['make_chapters', 'bool', 'false'],
            ['chapter_length', 'number', '8'],
        ]
    },
]


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
    log_file = '%s/logs/mediahandler.log' % os.path.expanduser("~")
    log_level = 40
    # Look for exceptions
    if settings['Logging']['log_file'] is not None:
        log_file = settings['Logging']['log_file']
    if settings['Logging']['level'] is not None:
        log_level = settings['Logging']['level']
    # Make sure log file dir exists
    log_path = os.path.dirname(log_file)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
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
    if (settings['TV']['enabled']
       or settings['Movies']['enabled']):
        settings['has_filebot'] = False
        # Check for Filebot
        if (not os.path.isfile('/usr/bin/filebot') and
                not os.path.isfile('/usr/local/bin/filebot')):
            raise ImportError('Filebot application not found')
        else:
            settings['has_filebot'] = True
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
            if not os.path.isfile('/usr/bin/abc.php'):
                raise ImportError('ABC application not found')
    return


# ======== PARSE CONFIG FILE ======== #

def parse_config(file_path):
    '''Read config file'''
    PARSER.read(file_path)
    settings = {}
    # Loop through config & validate
    for item in STRUCT:
        section = item['section']
        # Check that section exists
        if not PARSER.has_section(section):
            raise CP.NoSectionError(section)
        # Loop through options
        new_options = {}
        for item_option in item['options']:
            option = item_option[0]
            # Check that option exists
            if not PARSER.has_option(section, option):
                raise CP.NoOptionError(option, section)
            # Get valid option
            valid_func = "_get_valid_%s" % item_option[1]
            validator = getattr(util.config, valid_func)
            new_options[option] = validator(section, option)
        # Populate hash
        settings[section] = new_options
    # Check that appropriate modules are installed
    __check_modules(settings)
    # Return setting hash
    return settings


# ======== VALIDATION ======== #

# BOOLEAN
def _get_valid_bool(section, option):
    '''Validate config option as a boolean'''
    provided = PARSER.get(section, option)
    if provided == '':
        return False
    return PARSER.getboolean(section, option)


# STRING
def _get_valid_string(section, option):
    '''Validate config option as a string'''
    provided = PARSER.get(section, option)
    if provided == '':
        return None
    return provided


# NUMBER (INT)
def _get_valid_number(section, option):
    '''Validate config option as an int'''
    provided = PARSER.get(section, option)
    if provided == '':
        return None
    return PARSER.getint(section, option)


# PATH TO FILE
def _get_valid_file(section, option):
    '''Validate config option as a filepath'''
    provided = PARSER.get(section, option)
    if provided == '':
        return None
    folder = os.path.dirname(provided)
    if not os.path.exists(folder):
        error = ("Path to file provided for '%s: %s' does not exist: %s"
                 % (section, option, folder))
        raise CP.Error(error)
    return provided


# FOLDER
def _get_valid_folder(section, option):
    '''Validate config option as a folder'''
    provided = PARSER.get(section, option)
    if provided == '':
        return None
    if not os.path.exists(provided):
        error = ("Path provided for '%s: %s' does not exist: %s"
                 % (section, option, provided))
        raise CP.Error(error)
    return provided


# ======== MAKE CONFIG FILE ======== #

def make_config(new_file=None):
    '''Generate default config file'''
    # Set default path
    config_file = ('%s/.config/mediahandler/settings.conf' %
                   os.path.expanduser("~"))
    # Check for user-provided path
    if new_file is not None:
        config_file = new_file
    # Check that config exists
    if os.path.isfile(config_file):
        # Check config file permissions
        if not os.access(config_file, os.R_OK):
            raise Warning('Configuration file cannot be opened')
    else:
        # Setup sections and defaults
        for item in STRUCT:
            PARSER.add_section(item['section'])
            for option in item['options']:
                PARSER.set(item['section'], option[0], option[2])
        # Make directories for config file
        config_path = os.path.dirname(config_file)
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            os.chmod(config_path, 0775)
        # Write new configuration file to path
        with open(config_file, 'w') as config_file_open:
            PARSER.write(config_file_open)
    # Return with path to file
    return config_file
