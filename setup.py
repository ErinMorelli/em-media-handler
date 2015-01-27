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
    name='EM Media Handler',
    version='0.8.1',
    author='Erin Morelli',
    author_email='erin@erinmorelli.com',
    url='http://code.erinmorelli.com/em-media-handler/',
    license='GNU',
    platforms='Linux, OSX',
    description='A comprehensive media handling app.',
    long_description=open('README.rst').read(),
    test_suite='tests.testall.suite',
    package_dir={
        'mediahandler': 'mediahandler'
    },
    package_data={
        'mediahandler': [
            'extras/blacklist.txt',
            'extras/config.yml',
            'extras/require.yml',
            'extras/settings.yml',
        ]
    },
    packages=[
        'mediahandler',
        'mediahandler.types',
        'mediahandler.util',
    ],
    scripts=[
        'addmedia',
        'addmedia-deluge'
    ],
)

# Generate default config file
make_config()
