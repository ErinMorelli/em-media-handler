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
'''Main handler module'''

# ======== IMPORT MODULES ======== #

import re
import sys
import logging
from shutil import rmtree
from os import path, listdir, remove

import mediahandler as mh
import mediahandler.util.notify as Notify
import mediahandler.util.config as Config


# ======== DEFINE HANDLER CLASS ======== #

class Handler(object):
    '''Media handler class'''

    # ======== INIT CLASS ======== #

    def __init__(self, args_input):
        '''Initialize handler class'''
        # Set global variables
        self.args = {}
        self.settings = {}
        if not args_input:
            raise ValueError("Missing input arguments for Handler class")
        if type(args_input) is not dict:
            raise TypeError("Handler class arguments should be type dict")
        self.args = args_input
        # User-provided path
        __new_path = None
        # Check for user-specified config
        if 'config' in self.args.keys():
            __new_path = self.args['config']
        # Set paths
        __config_file = Config.make_config(__new_path)
        self.settings = Config.parse_config(__config_file)
        # Set up notify instance
        if 'no_push' not in self.args.keys():
            self.args['no_push'] = False
        self.push = Notify.Push(self.settings['Pushover'],
                                self.args['no_push'])
        # Media classes hash
        self.media_classes = {
            1: "Episode",
            2: "Movie",
            3: "Tracks",
            4: "Book"
        }

    # ======== MOVE VIDEO FILES ======== #

    def add_media_files(self, files):
        '''Process media files'''
        logging.info("Getting media information")
        # Set types
        itype = self.args['type']
        stype = self.args['stype']
        # Check for forced single import (Music)
        single = self.settings['single_file']
        if 'single_track' in self.args.keys():
            single = self.args['single_track']
        self.settings['Music']['single_track'] = single
        # Check for custom search (Audiobooks)
        if 'search' in self.args.keys():
            query = self.args['search']
            self.settings['Audiobooks']['custom_search'] = query
        # Check that type is enabled
        if not self.settings[stype]['enabled']:
            self.push.failure("%s type is not enabled" % stype)
        # Set module
        module = "mediahandler.types.%s" % stype.lower()
        logging.debug("Importing module: %s", module)
        # Import module
        __import__(module)
        mod = sys.modules[module]
        # Get class from module
        const = getattr(mod, self.media_classes[itype])
        logging.debug("Found class type: %s", const.__name__)
        # Initiate class
        media = const(self.settings[stype], self.push)
        logging.debug("Configured media type: %s", media.type)
        # Return
        return media.add(files)

    # ======== EXTRACT FILES ======== #

    def extract_files(self, raw):
        '''Send files to be extracted'''
        logging.info("Extracting files from compressed file")
        self.settings['extracted'] = raw
        # Look for filebot
        if 'has_filebot' in self.settings['TV'].keys():
            filebot = self.settings['TV']['has_filebot']
        elif 'has_filebot' in self.settings['Movies'].keys():
            filebot = self.settings['Movies']['has_filebot']
        else:
            self.push.failure("Filebot required to extract: %s"
                              % self.args['name'])
        # Import extract module
        import mediahandler.util.extract as Extract
        # Send to handler
        extracted = Extract.get_files(filebot, raw)
        if extracted is None:
            self.push.failure("Unable to extract files: %s"
                              % self.args['name'])
        # Send files back to handler
        return extracted

    # ======== FIND ZIPPED FILES ======== #

    def _find_zipped(self, files):
        '''Look for .zip, .rar, & .7z files'''
        logging.info("Looking for zipped files")
        file_string = files
        # Override if folder
        if not path.isfile(files):
            file_string = '\n'.join(listdir(files))
        # Set up regex
        flags = re.I | re.MULTILINE
        regex = r"^(.*.(zip|rar|7z))$"
        # Look for zipped files in file string
        if re.search(regex, file_string, flags):
            logging.debug("Zipped file type detected")
            # Send to extractor
            get_files = self.extract_files(files)
            # Rescan files
            self._file_handler(get_files)
        return

    # ======== REMOVE FILES ======== #

    def _remove_files(self, files, skip):
        '''Remove original files'''
        keep = self.settings['General']['keep_files']
        keep_skips = self.settings['General']['keep_if_skips']
        # Exit if we're not deleting anything
        if keep:
            return
        # Exit if we're keeping skipped files
        if skip and keep_skips:
            return
        # Otherwise, remove
        if path.exists(files):
            if 'extracted' in self.settings.keys():
                logging.debug("Removing extracted files folder")
                rmtree(self.settings['extracted'])
            if self.settings['single_file']:
                logging.debug("Removing extra single file")
                remove(files)
            else:
                logging.debug("Removing extra files folder")
                rmtree(files)
        return

    # ======== MAIN FILE HANDLER ======== #

    def _file_handler(self, files):
        '''Handle files by type'''
        logging.info("Starting files handler")
        # Look for zipped file first
        self._find_zipped(files)
        # Only set this flag for single files
        self.settings['single_file'] = False
        if path.isfile(files):
            self.settings['single_file'] = True
        # Make sure folders have files
        elif len(listdir(files)) == 0:
            self.push.failure("No %s files found for: %s" %
                              (self.args['stype'], self.args['name']))
        # Add files
        results = self.add_media_files(files)
        # Check results
        return self._check_success(files, results)

    # ======== CHECK FOR SUCCESS ======== #

    def _check_success(self, files, results):
        '''Check the results of add_media_files'''
        logging.info("Checking for success")
        skip = False
        # Extract results
        (added_files, skipped_files) = results
        # Make sure files were added
        if len(added_files) == 0 and len(skipped_files) == 0:
            self.push.failure("No %s files found for: %s" %
                              (self.args['stype'], self.args['name']))
        if len(skipped_files) > 0:
            skip = True
        # Remove old files
        self._remove_files(files, skip)
        # Finish & send success notification
        return self.push.success(added_files, skipped_files)

    # ======== CONVERT TYPE ======== #

    def _convert_type(self):
        '''Convert string type to int'''
        logging.info("Converting type")
        stype = ''
        # Make lowercase for comparison
        xtype = self.args['type'].lower()
        # Convert values
        if xtype in ['tv shows', 'television']:
            xtype = 'tv'
        elif xtype == 'books':
            xtype = 'audiobooks'
        # Look for int
        for key, value in mh.__mediakeys__.items():
            regex = r"%s" % value
            if re.match(regex, xtype, re.I):
                stype = value
                xtype = int(key)
                break
        # Store string & int values
        self.args['stype'] = stype
        self.args['type'] = xtype
        # Return
        logging.debug("Converted type: %s (%s)", stype, xtype)
        return

    # ======== PARSE DIRECTORY ======== #

    def _parse_dir(self, rawpath):
        '''Parse input directory structure'''
        logging.info("Extracing info from path: %s", rawpath)
        # Extract info from path
        parse_path = re.search(r"^((.*)?\/(.*))?\/(.*)$",
                               rawpath, re.I)
        if parse_path:
            self.args['path'] = parse_path.group(1)
            # Don't override a defined name
            if 'name' not in self.args.keys():
                self.args['name'] = parse_path.group(4)
            # Look for custom type
            if 'type' not in self.args.keys():
                self.args['type'] = parse_path.group(3)
                if self.args['type'].lower() not in mh.__mediatypes__:
                    self.push.failure('Media type %s not recognized'
                                      % self.args['type'])
            logging.debug("Type detected: %s", self.args['type'])
        else:
            logging.debug("No type detected")
            # Notify about failure
            self.push.failure(
                "No type or name specified for media: %s" %
                self.args['name'])
        # Convert type to number
        self._convert_type()
        return

    # ======== MAIN ADD MEDIA FUNCTION ======== #

    def add_media(self):
        '''Sort args based on input'''
        logging.debug("Inputs: %s", self.args)
        file_path = self.args['media']
        # Parse directory structure
        self._parse_dir(file_path)
        # Check that file was downloaded
        if path.exists(file_path):
            # Send to handler
            new_files = self._file_handler(file_path)
            # Check that files were returned
            if new_files is None:
                self.push.failure("No media files found: %s" %
                                  self.args['name'])
        else:
            # There was a problem, no files found
            self.push.failure("No media files found: %s" %
                              self.args['name'])
        return new_files
