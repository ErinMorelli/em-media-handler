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
'''
Module: mediahandler.handler

Module contains:

    - |MHandler|
        Main handler object structure which serves as an entry
        point for the entire module. Contains the core logic for dispatching
        media to add to their respective submodules for further handling.

    - |main()|
        Wrapper function for handling CLI input.

'''

import re
import sys
import logging
from shutil import rmtree
from os import path, listdir, remove

import mediahandler as mh
import mediahandler.util.args as Args
import mediahandler.util.notify as Notify
from mediahandler.util.config import make_config, parse_config


class MHandler(mh.MHObject):
    '''Main handler object structure which serves as an entry point for
    the entire module. Contains the core logic for dispatching media to add
    to their respective submodules for further handling.

    Required argument:

        - config
            Full path to valid mediahandler configuration file.
            A default file available for customization is located here: ::

              ~/.config/mediahandler/config.yml

    Public methods:

        - add_media()
            Main entry point containing the logic sequence for
            sending media files to the correct submodule processor.

        - extract_files()
            Wrapper function for accessing the
            mediahandler.util.extract module
    '''

    def __init__(self, config):
        '''Initialize the MHandler class.

        Required argument:

            - config
                Full path to valid mediahandler configuration file.
                A default file available for customization is located here: ::

                  ~/.config/mediahandler/config.yml
        '''

        # Set up args via super
        super(MHandler, self).__init__(config)

        # Extract settings from config
        self.config = make_config(config)
        self.set_settings(parse_config(self.config))

        # Set up notify instance
        self.push = Notify.MHPush(self.notifications)

        # Placeholders members
        self.single_file = False
        self.extracted = None

    def add_media(self, media, **kwargs):
        '''Entry point function for adding media via the MHandler object.

        Required argument:

            - media
                valid path to a file or a folder of media
                to be added. Assumes structure: ::

                  /path/to/<media type>/<media>

        Other valid arguments:

            - type
                Int in range [1, 2, 3, 4]. Declare a specific file type.
                Defaults to a <media type> derived from media path.
                Valid file types are:

                    * 1 - TV
                    * 2 - Movies
                    * 3 - Music
                    * 4 - Audiobooks

            - query
                String. Set a custom query string for audiobooks.
                Useful for fixing "Unable to match" errors.

            - single
                True/False. Force beets to import music as a single
                track. Useful for fixing "items were skipped" errors.

            - nopush
                True/False. Disable push notifications. Overrides
                the "enabled" config file setting.
        '''

        # Set object info from input
        self._parse_args_from_dict(media, **kwargs)
        logging.debug("Media: %s", self.media)

        # Check that file was downloaded
        if path.exists(self.media):
            # Send to handler
            new_files = self._file_handler(self.media)

            # Check that files were returned
            if new_files is None:
                self.push.failure(
                    "No media files found: {0}".format(self.name))

        # There was a problem, no files found
        else:
            self.push.failure(
                "No media files found: {0}".format(self.name))

        return new_files

    def _parse_args_from_dict(self, media, **kwargs):
        '''Validate arguments from the add_media() function via the CLI
        argparse object in the mediahandler.util.args module.

            - Checks to see if the arguments originate from the CLI via the
              'validated' flag. Skips argparse validation if True.

            - Updated the MHandler and MHPush object members with new values.
        '''

        # If we're already validated just set new arg values
        if 'validated' in kwargs.keys() and kwargs['validated']:
            kwargs['media'] = media
            if 'config' in kwargs.keys():
                del kwargs['config']
            new_args = kwargs

        # Send args to parser for validation
        else:
            new_args = Args.get_add_media_args(media, **kwargs)

        # Update MHandler object
        self.set_settings(new_args)

        # Update MHPush object, if necessary
        if hasattr(self, 'no_push'):
            self.push = Notify.MHPush(self.notifications, self.no_push)

        return

    def _file_handler(self, files):
        '''A wrapper function for _add_media_files().

            - Looks for and extracts zipped files
            - Sets single_file flag
            - Checks that media folder is not empty
            - Sends media files to _add_media_files()
            - Checks for success
        '''

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
        results = self._add_media_files(files)

        return self._check_success(files, results)

    def _find_zipped(self, files):
        '''Looks for compressed file types and sends them to extract_files().

        File types supported: .zip, .rar, .7z
        '''

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

    def extract_files(self, raw):
        '''Wrapper function for sending compressed files for extraction via
        the mediahandler.util.extract module.

        Requires the Filebot application for extraction.
        '''

        logging.info("Extracting files from compressed file")
        self.extracted = raw

        # Look for filebot
        if hasattr(self.tv, 'filebot'):
            filebot = self.tv.filebot
        elif hasattr(self.movies, 'filebot'):
            filebot = self.movies.filebot
        if not filebot:
            self.push.failure(
                "Filebot required to extract: {0}".format(self.name))

        # Import extract module
        import mediahandler.util.extract as Extract

        # Send to handler
        extracted = Extract.get_files(filebot, raw)
        if extracted is None:
            self.push.failure(
                "Unable to extract files: {0}".format(self.name))

        return extracted

    def _add_media_files(self, files):
        '''Sends media files to the correct mediahandler.types submodule
        based on media type.

        Derives submodule name and submodule MHMediaType subclass name from
        the 'stype' member value.
        '''

        logging.info("Getting media information")
        use_type = self.stype.lower()

        # Check for forced single import (Music)
        single = self.single_file
        if hasattr(self, 'single_track') and self.single_track:
            single = self.single_track
        self.music.single_track = single

        # Check for custom search (Audiobooks)
        if hasattr(self, 'query') and self.query is not None:
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
        const = getattr(mod, self._get_class_name())
        logging.debug("Found class type: %s", const.__name__)

        # Initiate class
        media = const(getattr(self, use_type), self.push)
        logging.debug("Configured media type: %s", media.type)

        return media.add(files)

    def _get_class_name(self):
        '''Return the MHMediaType subclass name based on the media type.
        '''
        use_type = re.sub(r's$', '', self.stype)

        return 'MH{0}'.format(use_type.capitalize())

    def _check_success(self, files, results):
        '''Checks and processes the output of _add_media_files().

        Sends files to be removed (if enabled). Documents added and skipped
        files then sends information to mediahandler.util.notify module.
        '''

        logging.info("Checking for success")
        skip = False

        # Extract results
        (added_files, skipped_files) = results

        # Make sure files were added
        if len(added_files) == 0 and len(skipped_files) == 0:
            self.push.failure(
                "No {0} files found for: {1}".format(self.stype, self.name))

        # Make note of any skips
        if len(skipped_files) > 0:
            skip = True

        # Remove old files
        self._remove_files(files, skip)

        return self.push.success(added_files, skipped_files)

    def _remove_files(self, files, skip):
        '''Removes left over files from processing.

        Checks user's 'keep_files' and 'keep_if_skips' settings. Removes
        any extracted files in addition to other left over files.
        '''

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

            # Remove any extracted files
            if self.extracted is not None:
                logging.debug("Removing extracted files folder")
                rmtree(self.extracted)

            # Remove a single file
            if self.single_file:
                logging.debug("Removing extra single file")
                remove(files)

            # Remove a folder
            else:
                logging.debug("Removing extra files folder")
                rmtree(files)

        return


def main(deluge=False):
    '''Wrapper function for passing CLI arguments to the MHandler
    add_media() function for processing.

    Optional argument:
        - deluge
            True/False. Determines whether basic argument
            parser or deluge argument parser should be used.
    '''

    # Get arguments
    (config, args) = Args.get_arguments(deluge)

    # Set up handler
    handler = MHandler(config)

    # Set up add media args
    added = handler.add_media(validated=True, **args)

    # Print for cmd line & return
    sys.stdout.write(added)
    return added
