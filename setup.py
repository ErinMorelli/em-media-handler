#!/usr/bin/python
#
# EM MEDIA HANDLER
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
'''Media handler module setup
'''

from setuptools import setup
from mediahandler.util.config import make_config


# Set up mediahandler package
setup(
    name = 'EM Media Handler',
    version = '1.0.1',
    author = 'Erin Morelli',
    author_email = 'erin@erinmorelli.com',
    url = 'http://code.erinmorelli.com/em-media-handler/',
    license = 'GNU',
    platforms = 'Linux, OSX',
    description = 'A comprehensive media handling automation script.',
    long_description = open('README.rst').read(),
    test_suite = 'tests.testall.suite',
    include_package_data = True,

    packages = [
        'mediahandler',
        'mediahandler.types',
        'mediahandler.util',
    ],

    entry_points = {
        'console_scripts': [
            'addmedia = mediahandler.handler:main',
        ],
    },

    scripts = [
        'addmedia-deluge'
    ],

    install_requires = [
        'google-api-python-client',
        'mutagen',
        'requests',
    ],

    extras_require = {
        'music': ['beets'],
        'deluge': ['twisted'],
    },
)

# Generate default config file
make_config()
