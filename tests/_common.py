#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
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
'''Common testing functions module'''

import string
import tempfile
from random import choice

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import mediahandler.util.config as Config


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
        name = "%s.tmp" % random_string(6)
    return tempfile.gettempdir() + '/' + name


def get_conf_file():
    return Config.make_config()


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


def get_test_api():
    return {
        'api_key': 'aHyetWak8sdc4nq1bWdyBKrCqwfon7',
        'user_key': 'uvdttD8roFNXYMpJuhfyKDmiwwsaUb',
    }
