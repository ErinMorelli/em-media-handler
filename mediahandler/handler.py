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
'''Main handler module'''

# ======== IMPORT MODULES ======== #

import sys
import logging
from re import search, match, I
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
                                self.args['use_deluge'],
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
        # Import extract module
        import mediahandler.util.extract as Extract
        # Send to handler
        extracted = Extract.get_files(raw)
        if extracted is None:
            self.push.failure("Unable to extract files: %s"
                              % self.args['name'])
        # Send files back to handler
        return extracted

    # ======== SINGLE FILE HANDLER ======== #

    def __single_file(self, files):
        '''Process single files'''
        # Single file, treat differently
        logging.debug("Processing as a single file")
        self.settings['single_file'] = True
        # Look for zipped file first
        if search(r".(zip|rar|7z)$", files, I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.settings['has_filebot']:
                get_files = self.extract_files(files)
                # Rescan files
                self.__file_handler(get_files)
        # otherwise treat like other files
        return self.add_media_files(files)

    # ======== FOLDER HANDLER ======== #

    def __process_folder(self, files):
        '''Process as folder'''
        # Otherwise process as folder
        logging.debug("Processing as a folder")
        self.settings['single_file'] = False
        # Get a list of files
        file_list = listdir(files)
        # Look for zipped file first
        if search(r".(zip|rar|7z)\n", '\n'.join(file_list), I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.settings['has_filebot']:
                get_files = self.extract_files(files)
                # Rescan files
                self.__file_handler(get_files)
        # Check for music
        if self.args['type'] is 3:
            return self.add_media_files(files)
        else:
            # Locate video file in folder
            for item in file_list:
                # Look for file types we want
                if search(r"\.(mkv|avi|m4v|mp4)$", item, I):
                    # Set info
                    file_name = item
                    src = files+'/'+file_name
                    # Move file
                    return self.add_media_files(src)

    # ======== REMOVE FILES ======== #

    def __remove_files(self, files, skip):
        '''Remove original files'''
        keep = self.settings['General']['keep_files']
        keep_dups = self.settings['General']['keep_if_duplicates']
        # Exit if we're not deleting anything
        if keep:
            return
        # Exit if we're keeping duplicates
        if skip and keep_dups:
            return
        # Otherwise, remove
        if path.exists(files):
            if 'extracted' in self.settings.keys():
                logging.debug("Removing extracted files folder")
                rmtree(self.settings['extracted'])
            elif self.settings['single_file']:
                logging.debug("Removing extra single file")
                remove(files)
            else:
                logging.debug("Removing extra files folder")
                rmtree(files)
        return

    # ======== MAIN FILE HANDLER ======== #

    def __file_handler(self, files):
        '''Handle files by type'''
        logging.info("Starting files handler")
        added_files = []
        added_file = ''
        skipped_files = []
        skip = False
        # Process books first
        if self.args['type'] is 4:
            (added_file, skip) = self.add_media_files(files)
        # Then check for folders/files
        elif path.isfile(files):
            (added_file, skip) = self.__single_file(files)
        else:
            (added_file, skip) = self.__process_folder(files)
        # Update file arrays
        if skip:
            skipped_files.append(added_file)
        else:
            added_files.append(added_file)
        # Make sure files were added
        if len(added_files) == 0 and len(skipped_files) == 0:
            self.push.failure("No %s files found for: %s" %
                              (self.args['stype'], self.args['name']))
        # Remove old files
        self.__remove_files(files, skip)
        # Send success notification
        self.push.success(added_files, skipped_files)
        # Finish
        return added_files

    # ======== CONVERT TYPE ======== #

    def __convert_type(self):
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
            if match(regex, xtype, I):
                stype = value
                xtype = int(key)
                break
        # Store string & int values
        self.args['stype'] = stype
        self.args['type'] = xtype
        # Return
        logging.debug("Converted type - %s, %s", xtype, stype)
        return

    # ======== PARSE DIRECTORY ======== #

    def __parse_dir(self, rawpath):
        '''Parse input directory structure'''
        logging.info("Extracing info from path: %s", rawpath)
        # Extract info from path
        parse_path = search(r"^((.*)?\/(.*))?\/(.*)$",
                            rawpath, I)
        if parse_path:
            self.args['path'] = parse_path.group(1)
            # Don't override deluge-defined name
            if 'name' not in self.args.keys():
                self.args['name'] = parse_path.group(4)
            # Look for custom type
            if 'type' not in self.args.keys():
                self.args['type'] = parse_path.group(3)
                if self.args['type'].lower() not in mh.__mediatypes__:
                    self.push.failure('Media type %s not recognized'
                                      % self.args['type'], True)
            logging.debug("Type detected: %s", self.args['type'])
        else:
            logging.debug("No type detected")
            if self.settings['Deluge']['enabled']:
                # Remove torrent
                import mediahandler.util.torrent as Torrent
                Torrent.remove_torrent(
                    self.settings['Deluge'],
                    self.args['hash'])
            # Notify about failure
            self.push.failure(
                "No type or name specified for media: %s" %
                self.args['name'], True)
        # Convert type to number
        self.__convert_type()
        return

    # ======== HANDLE MEDIA ======== #

    def __handle_media(self):
        '''Sort args based on input'''
        logging.debug("Inputs: %s", self.args)
        # Determing if using deluge or not
        file_path = ''
        use_deluge = self.args['use_deluge']
        if use_deluge:
            logging.info("Processing from deluge")
            file_path = path.join(self.args['path'], self.args['name'])
        else:
            logging.info("Processing from command line")
            file_path = self.args['media']
        # Parse directory structure
        self.__parse_dir(file_path)
        # Check that file was downloaded
        if path.exists(file_path):
            if self.settings['Deluge']['enabled'] and use_deluge:
                # Remove torrent
                import mediahandler.util.torrent as Torrent
                Torrent.remove_torrent(
                    self.settings['Deluge'],
                    self.args['hash'])
            # Send to handler
            new_files = self.__file_handler(file_path)
            # Check that files were returned
            if new_files is None:
                self.push.failure("No media files found: %s" %
                                  self.args['name'], True)
        else:
            # There was a problem, no files found
            self.push.failure("No media files found: %s" %
                              self.args['name'], True)
        return new_files

    # ======== MAIN ADD MEDIA FUNCTION ======== #

    def add_media(self):
        '''Main function'''
        # Start main function
        new_files = self.__handle_media()
        # Exit
        return new_files
