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
'''Command line & scripting interface'''


# ======== IMPORT MODULES ======== #

import mediahandler.handler as mh


# ======== COMMAND LINE ======== #

if __name__ == '__main__':
    h = mh.Handler()
    added_files = h.addmedia()
    if len(added_files) > 0:
        print "\nMedia successfully added!\n"
        for a in added_files:
            print "\t%s" % str(a)
        print "\n"
    else:
        raise Warning("No media added")
