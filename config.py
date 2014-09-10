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

import ConfigParser as cp


# ======== CONFIG CLASS DECLARTION ======== #

class mhConfig:

	# ======== SET GLOBAL CLASS OPTIONS ======== #

	def __init__(self):
		config = cp.SafeConfigParser()
		config.read('mediaHandler.conf')
		print config.get('My Section', 'foodir')
		return

c = mhConfig()