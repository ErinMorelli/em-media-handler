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
from mediahandler.util.config import make_config, parse_config


# ======== DEFINE HANDLER CLASS ======== #

class MHandler(mh.MHObject):
    '''Media handler class'''

    # ======== INIT CLASS ======== #

    def __init__(self, args):
        '''Initialize handler class'''
        super(MHandler, self).__init__(args)
        # Check args
        if not args:
            raise ValueError("Missing input arguments for Handler class")
        # Extract settings from config
        self.config = make_config(self.config)
        self._set_settings(parse_config(self.config))
        # Set up notify instance
        self.push = Notify.MHPush(self.pushover, self.no_push)
        
        # Placeholders
        self.single_file = False
        self.extracted = None

    # ======== MOVE VIDEO FILES ======== #

    def _get_object_name(self):
        '''Return module name based on type'''
        use_type = re.sub(r's$', '', self.stype)
        return 'MH{0}'.format(use_type.capitalize())

    # ======== MOVE VIDEO FILES ======== #

    def add_media_files(self, files):
        '''Process media files'''
        logging.info("Getting media information")
        use_type = self.stype.lower()
        # Check for forced single import (Music)
        single = self.single_file
        if self.single_track:
            single = self.single_track
        self.music.single_track = single
        # Check for custom search (Audiobooks)
        if self.query is not None:
            self.audiobooks.custom_search = self.query
        # Check that type is enabled
        if not getattr(self, use_type).enabled:
            self.push.failure("{0} type is not enabled".format(self.stype))
        # Set module
        module = "mediahandler.types.{0}".format(use_type)
        logging.debug("Importing module: %s", module)
        # Import module
        __import__(module)
        mod = sys.modules[module]
        # Get class from module
        const = getattr(mod, self._get_object_name())
        logging.debug("Found class type: %s", const.__name__)
        # Initiate class
        media = const(getattr(self, use_type), self.push)
        logging.debug("Configured media type: %s", media.type)
        # Return
        return media.add(files)

    # ======== EXTRACT FILES ======== #

    def extract_files(self, raw):
        '''Send files to be extracted'''
        logging.info("Extracting files from compressed file")
        self.extracted = raw
        # Look for filebot
        if hasattr(self.tv, 'filebot'):
            filebot = self.tv.filebot
        elif hasattr(self.movies, 'filebot'):
            filebot = self.movies.filebot
        else:
            self.push.failure(
                "Filebot required to extract: {0}".format(self.name))
        # Import extract module
        import mediahandler.util.extract as Extract
        # Send to handler
        extracted = Extract.get_files(filebot, raw)
        if extracted is None:
            self.push.failure(
                "Unable to extract files: {0}".format(self.name))
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
        keep = self.general.keep_files
        keep_skips = self.general.keep_if_skips
        # Exit if we're not deleting anything
        if keep:
            return
        # Exit if we're keeping skipped files
        if skip and keep_skips:
            return
        # Otherwise, remove
        if path.exists(files):
            if self.extracted is not None:
                logging.debug("Removing extracted files folder")
                rmtree(self.extracted)
            if self.single_file:
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
        if path.isfile(files):
            self.single_file = True
        # Make sure folders have files
        elif len(listdir(files)) == 0:
            self.push.failure(
                "No {0} files found for: {1}".format(self.stype, self.name))
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
            self.push.failure(
                "No {0} files found for: {1}".format(self.stype, self.name))
        if len(skipped_files) > 0:
            skip = True
        # Remove old files
        self._remove_files(files, skip)
        # Finish & send success notification
        return self.push.success(added_files, skipped_files)

    # ======== MAIN ADD MEDIA FUNCTION ======== #

    def add_media(self):
        '''Sort args based on input'''
        logging.debug("Media: %s", self.media)
        # Check that file was downloaded
        if path.exists(self.media):
            # Send to handler
            new_files = self._file_handler(self.media)
            # Check that files were returned
            if new_files is None:
                self.push.failure(
                    "No media files found: {0}".format(self.name))
        else:
            # There was a problem, no files found
            self.push.failure(
                "No media files found: {0}".format(self.name))
        return new_files
