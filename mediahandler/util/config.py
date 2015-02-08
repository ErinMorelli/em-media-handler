#!/usr/bin/python
#
# This file is a part of EM Media Handler
# Copyright (c) 2014-2015 Erin Morelli
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
'''
Module: mediahandler.util.config

Module contains:

    - |make_config()|
        Generates a default yaml configuration file.

    - |parse_config()|
        Parses a yaml configuration file and returns a dict of the settings.

'''

import os
import imp
import shutil
import logging

import mediahandler as mh
import mediahandler.util as Util

try:
    import yaml
except ImportError:
    pass


def make_config(new_file=None):
    '''Generates default yaml mediahandler configuration file.

    Optional argument:
        - new_file
            Path to a yaml mediahandler configuration file. Will
            verify that the file exists and is readable.
    '''

    # Set default path
    config_file = os.path.join(os.path.expanduser("~"),
                               '.config', 'mediahandler', 'config.yml')

    # Check for user-provided path
    if new_file is not None:
        config_file = new_file

    # Check that config exists
    if os.path.isfile(config_file):

        # Check config file permissions
        if not os.access(config_file, os.R_OK):
            raise Warning('Configuration file cannot be opened')

    else:
        # Copy default config to user file
        default_config = os.path.join(mh.__mediaextras__, 'config.yml')

        # Make directories for config file
        config_path = os.path.dirname(config_file)
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            os.chmod(config_path, 0o775)

        # Copy new configuration file to path
        shutil.copy(default_config, config_file)

        # Change permissions to current user if sudo
        if 'SUDO_UID' in os.environ.keys():
            filed = os.open(config_file, os.O_RDONLY)
            os.fchown(filed, int(os.environ['SUDO_UID']), -1)
            os.close(filed)

    return config_file


def parse_config(file_path):
    '''Reads and parses a yaml mediahandler configuration file.

    Optional argument:
        - file_path
            Path to a valid yaml mediahandler configuration file.

    Uses settings.yml validation structure to build missing and default
    values. Sends values to the correct _get_valid_<type>() function
    for validation.
    '''

    # Read yaml files
    parsed = _get_yaml(file_path)
    struct = _get_yaml(os.path.join(mh.__mediaextras__, 'settings.yml'))

    # Define section function
    def _process_section(get_section, get_options, get_parsed):
        '''Processes a section of yaml options.

        Sets the default value for the option if unset. Dispatches value to
        correct validation function.
        '''

        # Make section if it doesn't exist
        if get_section not in get_parsed.keys():
            get_parsed[get_section] = {}

        # Look through options
        new_options = {}
        for item_option in get_options:
            option = item_option['name']
            value = ''

            # Is this a section, process children
            if item_option['type'] == 'section':
                new_options[option] = _process_section(
                    item_option['name'],
                    item_option['options'],
                    get_parsed[get_section])
                continue

            # If option exists, get value
            elif option in get_parsed[get_section].keys():
                value = get_parsed[get_section][option]

            # Otherwise use default
            elif 'default' in item_option.keys():
                value = item_option['default']

            # Fallback to non
            else:
                new_options[option] = None
                continue

            # Validate values
            valid_func = "_get_valid_{0}".format(item_option['type'])
            validator = getattr(Util.config, valid_func)
            new_options[option] = validator(get_section, option, value)

        return new_options

    # Loop through config & validate
    settings = {}
    for item in struct['items']:
        section = item['section']

        # Populate hash
        settings[section] = _process_section(
            section, item['options'], parsed)

    # Check that appropriate modules are installed
    _check_modules(settings)

    return settings


# Settings option validation functions

def _get_valid_bool(section, option, provided):
    '''Validates a boolean type configuration option.

    Returns False by default if the option is unset.
    '''

    if provided is None:
        return False

    if type(provided) is not bool:
        error = "Value provided for '{0}: {1}' is not a valid boolean".format(
            section, option)
        raise ValueError(error)

    return provided


def _get_valid_string(section, option, provided):
    '''Validates a string type configuration option.

    Returns None by default if the option is unset.
    '''

    if provided is None:
        return None

    if type(provided) is not str:
        error = "Value provided for '{0}: {1}' is not a valid string".format(
            section, option)
        raise ValueError(error)

    return provided


def _get_valid_number(section, option, provided):
    '''Validates an int type configuration option.

    Returns None by default if the option is unset.
    '''

    if provided is None:
        return None

    try:
        return int(provided)

    except ValueError:
        error = "Value provided for '{0}: {1}' is not a valid number".format(
            section, option)
        raise ValueError(error)


def _get_valid_file(section, option, provided):
    '''Validates a file type configuration option.

    Returns None by default if the option is unset.
    '''

    if provided is None:
        return None

    folder = os.path.dirname(provided)

    if not os.path.exists(folder):
        error = "File path provided for '{0}: {1}' does not exist: {2}".format(
            section, option, folder)
        raise ValueError(error)

    return provided


def _get_valid_folder(section, option, provided):
    '''Validates a folder type configuration option.

    Returns None by default if the option is unset.
    '''

    if provided is None:
        return None

    if not os.path.exists(provided):
        error = "Path provided for '{0}: {1}' does not exist: {2}".format(
            section, option, provided)
        raise ValueError(error)

    return provided


# Configuration parse helper functions

def _get_yaml(yaml_file):
    '''Retrieves and parses a yaml file.
    '''

    # Read yaml file
    yaml_contents = open(yaml_file).read()

    # Decode yaml
    contents = yaml.load(yaml_contents)

    return contents


def _init_logging(settings):
    '''Turns on logging for the mediahandler object.

    User the 'log_file' and 'level' settings from the user
    configuration file for setup.
    '''

    # Set defaults
    log_file = os.path.join(
        os.path.expanduser("~"), 'logs', 'mediahandler.log')
    log_level = 30

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
        from deluge import log
        log.setupLogger()

    return


def _check_modules(settings):
    '''Looks for modules and applications required by user-enabled options.

    Uses the require.yml settings to determine which python modules or third-
    party applications are needed for a given enabled option and then checks
    the user's system to see if they are installed.
    '''

    # Check for logging
    if settings['Logging']['enabled']:
        _init_logging(settings)
        logging.info('Logging enabled')

    # Retrieve module info from yaml file
    require = _get_yaml(os.path.join(mh.__mediaextras__, 'require.yml'))

    # Look for modules & apps
    for section in require:
        item = require[section]
        option = item['option']

        # Check if the requirement condition is met
        if settings[section][option]:

            # Check modules
            if 'modules' in item.keys():
                for module in item['modules']:
                    _find_module(module[0], module[1])

            # Check applications
            if 'apps' in item.keys():
                for app in item['apps']:
                    _find_app(settings[section], app)

    return


def _find_module(parent_mod, sub_mod):
    '''Attempts to load a python module.

    Raises an ImportError if a python module and submodule is not installed
    on the user's system.
    '''

    try:
        # Look attempt to load module
        mod_info = imp.find_module(parent_mod)
        mod = imp.load_module(parent_mod, *mod_info)
        imp.find_module(sub_mod, mod.__path__)

        return True

    except ImportError:
        # Otherwise raise an Import error
        err_msg = 'Module {0}.{1} is not installed'.format(parent_mod, sub_mod)

        raise ImportError(err_msg)


def _find_app(settings, app):
    '''Looks for an installed application in the user's local $PATH.

    Raises an ImportError if the application is not found.
    '''

    # Save in settings
    name = app['name'].lower()
    settings[name] = None

    # Retrieve local paths
    local_paths = os.environ['PATH'].rsplit(':')

    # Look for app in local paths
    for local_path in local_paths:
        path = os.path.join(local_path, app['exec'])

        # If the path exists, store & exit the loop
        if os.path.isfile(path):
            settings[name] = path
            break

    # If app not found, raise ImportError
    if settings[name] is None:
        error = '{0} application not found'.format(app['name'])
        raise ImportError(error)

    return
