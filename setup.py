#!/usr/bin/env python
# -*- coding: utf-8 -*-

# EM MEDIA HANDLER
# Copyright (c) 2014-2019 Erin Morelli
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
"""Media handler module setup
"""

import os
from setuptools import setup
from mediahandler.util.config import make_config

# Set up extra scripts
_extra_scripts = []
if os.name == 'nt':
    _extra_scripts.append('addmedia-deluge.bat')

# Set up mediahandler package
setup(
    name='em-media-handler',
    version='1.2',
    author='Erin Morelli',
    author_email='me@erin.dev',
    url='http://www.erinmorelli.com/projects/em-media-handler/',
    license='MIT',
    platforms='Linux, OSX, Windows',
    description='A comprehensive media handling automation script.',
    long_description=open('README.md').read(),
    test_suite='tests.testall.suite',
    include_package_data=True,

    packages=[
        'mediahandler',
        'mediahandler.types',
        'mediahandler.util',
    ],

    entry_points={
        'console_scripts': [
            'addmedia=mediahandler.handler:main',
            'addmedia-deluge=mediahandler.handler:deluge'
        ]
    },
    scripts=_extra_scripts,

    install_requires=[
        'pyyaml',
        'google-api-python-client',
        'mutagen',
        'oauth2client<=3.0.0',
        'setuptools>=40.3.0',
        'requests'
    ],

    extras_require={
        'music': [
            'beets',
            'pylast==2.3.0'
        ],
        'deluge': [
            'twisted',
            'pyopenssl'
        ],
    },

    tests_require=[
        'unittest2',
        'responses',
        'mock'
    ],

    classifiers=[
        'Topic :: Home Automation',
        'Topic :: Multimedia',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Environment :: MacOS X',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
    ],
)

# Generate default config file
make_config()
