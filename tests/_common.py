#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
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
'''Common testing functions module'''

import os
import shutil
import string
import tempfile
from random import choice

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mediahandler.util.config as Config


class MHTestSuite(unittest.TestSuite):

    def setUpSuite(self):
        # Back up current config
        curr_config = get_conf_file()
        backup = os.path.join(
            os.path.dirname(curr_config), 'config.yml.orig') 
        if not os.path.exists(backup):
            shutil.move(curr_config, backup)
        # Make new config for testing
        new_config = Config.make_config()

    def tearDownSuite(self):
        # Restore original config
        curr_config = get_conf_file()
        backup = os.path.join(
            os.path.dirname(curr_config), 'config.yml.orig') 
        if os.path.exists(backup):
            shutil.move(backup, curr_config)

    def run(self, result):
        # Before tests
        self.setUpSuite()
        # Set buffering
        result.buffer = True
        # Run tests
        super(MHTestSuite, self).run(result)
        # After tests
        self.tearDownSuite()


def skipUnlessHasMod(module, submodule):
    try:
        Config._find_module(module, submodule)
    except ImportError:
        return unittest.skip("requires module {0}.{1}".format(module, submodule))
    else:
        return lambda func: func


def get_test_id(size=4):
    num = []
    while size > 0:
        x = choice('0123456789')
        num.append(x)
        size -= 1
    return ''.join(num)


def random_string(size=5):
    chars = string.ascii_uppercase + string.digits
    return ''.join(choice(chars) for x in range(size))


def temp_file(name=None):
    if name is None:
        name = "{0}.tmp".format(random_string(6))
    return os.path.join(tempfile.gettempdir(), name)


def make_tmp_file(text=None, tdir=None):
    if tdir is None:
        tdir = os.path.dirname(get_conf_file())
    if text is None:
        text = '.tmp'
    get_file = tempfile.NamedTemporaryFile(
            dir=tdir,
            suffix=text,
            delete=False)
    return get_file.name


def get_conf_file():
    return Config.make_config()


def get_orig_settings():
    conf_dir = os.path.dirname(get_conf_file())
    old_config = os.path.join(conf_dir, 'config.yml.orig')
    if not os.path.exists(old_config):
        old_config = os.path.join(conf_dir, 'config.yml')
    return get_settings(old_config)


def get_settings(conf=None):
    if conf is None:
        conf = get_conf_file()
    return Config.parse_config(conf)


def get_types_by_string():
    return {
        'TV': 1,
        'Movies': 2,
        'Music': 3,
        'Audiobooks': 4
    }


def get_types_by_id():
    return {
        1: 'TV',
        2: 'Movies',
        3: 'Music',
        4: 'Audiobooks'
    }


def get_pushover_api():
    apis = {}
    
    # Get API Key
    if 'PUSHOVER_API_KEY' in os.environ.keys():
        apis['api_key'] = os.environ['PUSHOVER_API_KEY']
    else:
        apis['api_key'] = get_orig_settings()['Pushover']['api_key']
    # Get User Key
    if 'PUSHOVER_USER_KEY' in os.environ.keys():
        apis['user_key'] = os.environ['PUSHOVER_USER_KEY']
    else:
        apis['user_key'] = get_orig_settings()['Pushover']['user_key']
    return apis


def get_google_api():
    if 'GOOGLE_API_KEY' in os.environ.keys():
        return os.environ['GOOGLE_API_KEY']
    else:
        return get_orig_settings()['Audiobooks']['api_key']
