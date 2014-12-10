#!/usr/bin/python
#
# EM MEDIA HANDLER
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
'''Media handler module setup'''


# ======== IMPORT MODULES ======== #

from distutils.core import setup
from mediahandler.util.config import makeconfig


# ======== MODULE SETUP ======== #

setup(
    name='EM Media Handler',
    version='0.3.2',
    author='Erin Morelli',
    author_email='erin@erinmorelli.com',
    url='http://code.erinmorelli.com/em-media-handler/',
    license='GNU',
    platforms='Linux',
    description='A comprehensive media library manager.',
    long_description=open('README.rst').read(),
    package_dir={'mediahandler': 'mediahandler'},
    package_data={'mediahandler': ['types/blacklist.txt']},
    packages=[
        'mediahandler',
        'mediahandler.types',
        'mediahandler.util'],
    scripts=['addmedia'],
)

# Generate default config file
makeconfig(None)
