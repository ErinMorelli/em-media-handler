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
import re
import sys

from _common import unittest
from _common import MHTestSuite

pkgpath = os.path.dirname(__file__) or '.'
sys.path.append(pkgpath)


def suite():
    s = MHTestSuite()
    for fname in os.listdir(pkgpath):
        match = re.match(r'(test_\S+)\.py$', fname)
        if match:
            modname = match.group(1)
            s.addTest(__import__(modname).suite())
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
