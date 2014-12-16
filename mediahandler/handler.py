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

import logging
from re import search, I
from shutil import rmtree
from os import path, listdir, remove
import mediahandler as mh
import mediahandler.util.notify as Notify
from mediahandler.util.config import getconfig, makeconfig


# ======== DEFINE HANDLER CLASS ======== #

class Handler:
    '''Media handler class'''
    # ======== INIT CLASS ======== #

    def __init__(self, args_input):
        '''Initialize handler class'''
        # Set global variables
        self.args = args_input
        self.settings = {}
        self.push = ''
        # User-provided path
        __new_path = None
        # Check for user-specified config
        if 'config' in self.args.keys():
            __new_path = self.args['config']
        # Set paths
        __config_path = makeconfig(__new_path)
        # Get settings from config
        self.settings = getconfig(__config_path)
        # Set up notify instance
        self.push = Notify.Push(self.settings['Pushover'],
                                args_input['use_deluge'])

    # ======== GETTERS ======== #

    def get_args(self):
        '''Get all arguments'''
        return self.args

    def get_arg(self, key):
        '''Get argument by key'''
        return self.args[key]

    def get_settings(self):
        '''Get all settings'''
        return self.settings

    def get_setting(self, key, sub_key=None):
        '''Get setting by key and sub key'''
        if sub_key is not None:
            return self.settings[key][sub_key]
        else:
            return self.settings[key]

    def get_push(self):
        '''Get push class object'''
        return self.push

    # ======== SETTERS ======== #

    def set_arg(self, value, key):
        '''Set argument by key and value'''
        self.args[key] = value
        return

    def set_setting(self, value, key, sub_key=None):
        '''Set setting by key, sub key, and value'''
        if sub_key is not None:
            self.settings[key][sub_key] = value
        else:
            self.settings[key] = value
        return

    # ======== MOVE VIDEO FILES ======== #

    def add_video(self, src):
        '''Process video files'''
        logging.info("Moving file(s)")
        # Set which handler to use
        if self.get_arg('type') in ["TV", "Television", "TV Shows"]:
            (new_name, dst) = self.add_episode(src)
        elif self.get_arg('type') == 'Movies':
            (new_name, dst) = self.add_movie(src)
        # Check for errors
        if new_name is None:
            return None
        logging.debug("Name: %s", new_name)
        logging.debug("DST: %s", dst)
        # Check that new file exists
        if not path.isfile(dst):
            self.get_push().failure("File failed to move: %s"
                                    % self.get_arg('name'))
        # Return new file name
        return new_name

    # ======== ADD TV EPISODE ======== #

    def add_episode(self, raw):
        '''Get and process TV episode information'''
        logging.info("Getting TV episode information")
        # Check that TV is enabled
        if not self.get_setting('TV', 'enabled'):
            self.get_push().failure("TV type is not enabled")
        # Import TV module
        import mediahandler.types.tv as TV
        # Send info to handler
        (ep_title, new_file) = TV.get_episode(raw, self.get_setting('TV'))
        if ep_title is None:
            self.get_push().failure("Unable to match episode: %s"
                                    % self.get_arg('name'))
        # return folder and file paths
        return ep_title, new_file

    # ======== ADD MOVIE ======== #

    def add_movie(self, raw):
        '''Get and process movie information'''
        logging.info("Getting movie information")
        # Check that Movies are enabled
        if not self.get_setting('Movies', 'enabled'):
            self.get_push().failure("Movies type is not enabled")
        # Import movie module
        import mediahandler.types.movies as Movies
        # Send info to handler
        (mov_title, new_file) = Movies.get_movie(raw,
                                                 self.get_setting('Movies'))
        if mov_title is None:
            self.get_push().failure("Unable to match movie: %s"
                                    % self.get_arg('name'))
        # return folder and file paths
        return mov_title, new_file

    # ======== ADD MUSIC ======== #

    def add_music(self, raw, is_single=False):
        '''Get and process music information'''
        logging.info("Getting music information")
        # Check that Movies are enabled
        if not self.get_setting('Movies', 'enabled'):
            self.push.failure("Movies type is not enabled")
        # Check for forced single import
        if 'single_track' in self.get_args().keys():
            is_single = self.get_arg('single_track')
        # Import music module
        import mediahandler.types.music as Music
        # Send info to handler
        music_return = Music.get_music(raw,
                                       self.get_setting('Music'), is_single)
        (has_skips, music_info) = music_return
        # Check for no info
        if music_info is None:
            self.get_push().failure(
                "Unable to match music: %s" % self.get_arg('name'))
        # Don't remove files if has skips
        if has_skips:
            self.set_setting(True, 'General', 'keep_files')
        # return album info
        return music_info

    # ======== ADD AUDIOBOOK ======== #

    def add_book(self, raw):
        '''Get and process book information'''
        logging.info("Getting audiobook information")
        # Set custom search query, if defined
        custom_search = None
        if 'search' in self.get_args().keys():
            custom_search = self.get_arg('search')
        # Check that Movies are enabled
        if not self.get_setting('Audiobooks', 'enabled'):
            self.push.failure("Audiobooks type is not enabled")
        # Import audiobooks module
        import mediahandler.types.audiobooks as Audiobooks
        # Send to handler
        bok = Audiobooks.Book(self.get_setting('Audiobooks'))
        book_info = bok.get_book(raw, custom_search)
        if book_info is None:
            self.get_push().failure("Unable to match book: %s"
                                    % self.get_arg('name'))
            return None
        # return book info
        return book_info

    # ======== EXTRACT FILES ======== #

    def extract_files(self, raw):
        '''Send files to be extracted'''
        logging.info("Extracting files from compressed file")
        self.set_setting(raw, 'extracted')
        # Import extract module
        import mediahandler.util.extract as Extract
        # Send to handler
        extracted = Extract.get_files(raw)
        if extracted is None:
            self.get_push().failure("Unable to extract files: %s"
                                    % self.get_arg('name'))
            return None
        # Send files back to handler
        return extracted

    # ======== SINGLE FILE HANDLER ======== #

    def __single_file(self, files):
        '''Process single files'''
        # Single file, treat differently
        logging.debug("Processing as a single file")
        self.set_setting(True, 'is_single')
        # Look for zipped file first
        if search(r".(zip|rar|7z)$", files, I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.get_setting('has_filebot'):
                get_files = self.extract_files(files)
                # Check for failure
                if get_files is None:
                    return None
                # Rescan files
                self.__file_handler(get_files)
        # otherwise treat like other files
        if self.get_arg('type') == "Music":
            return self.add_music(files, self.get_setting('is_single'))
        else:
            # Set single file as source
            src = files
            # Move file
            video_info = self.add_video(src)
            # Check for problems
            if video_info is None:
                return
            return video_info

    # ======== FOLDER HANDLER ======== #

    def __process_folder(self, files):
        '''Process as folder'''
        # Otherwise process as folder
        logging.debug("Processing as a folder")
        # Get a list of files
        file_list = listdir(files)
        # Look for zipped file first
        if search(r".(zip|rar|7z)\n", '\n'.join(file_list), I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.get_setting('has_filebot'):
                get_files = self.extract_files(files)
                # Check for failure
                if get_files is None:
                    return None
                # Rescan files
                self.__file_handler(get_files)
        # Check for music
        if self.get_arg('type') == "Music":
            return self.add_music(files)
        else:
            # Locate video file in folder
            for item in file_list:
                # Look for file types we want
                if search(r"\.(mkv|avi|m4v|mp4)$", item, I):
                    # Set info
                    file_name = item
                    src = files+'/'+file_name
                    # Move file
                    video_info = self.add_video(src)
                    # Check for problems
                    if video_info is None:
                        return
                    return video_info

    # ======== MAIN FILE HANDLER ======== #

    def __file_handler(self, files):
        '''Handle files by type'''
        logging.info("Starting files handler")
        added_files = []
        self.set_setting(False, 'is_single')
        # Process books first
        if self.get_arg('type') in ["Books", "Audiobooks"]:
            added_file = self.add_book(files)
            added_files.append(added_file)
        # Then check for folders/files
        elif path.isfile(files):
            added_file = self.__single_file(files)
            added_files.append(added_file)
        else:
            added_file = self.__process_folder(files)
            added_files.append(added_file)
        # Make sure files were added
        if len(added_files) == 0:
            self.get_push().failure("No %s files found for: %s" %
                                    (self.get_arg('type'),
                                     self.get_args('name')))
        # Remove old files
        if not self.get_setting('General', 'keep_files'):
            if path.exists(files):
                if 'extracted' in self.get_settings().keys():
                    logging.debug("Removing extracted files folder")
                    rmtree(self.get_setting('extracted'))
                elif self.get_setting('is_single'):
                    logging.debug("Removing extra single file")
                    remove(files)
                else:
                    logging.debug("Removing extra files folder")
                    rmtree(files)
        # Send success notification
        self.get_push().success(added_files)
        # Finish
        return added_files

    # ======== PARSE DIRECTORY ======== #

    def __parse_dir(self, rawpath):
        '''Parse input directory structure'''
        logging.info("Extracing info from path")
        logging.debug(rawpath)
        # Extract info from path
        parse_path = search(r"^((.*)?\/(.*))?\/(.*)$",
                            rawpath, I)
        if parse_path:
            self.set_arg(parse_path.group(1), 'path')
            # Don't override deluge-defined name
            if 'name' not in self.get_args().keys():
                self.set_arg(parse_path.group(4), 'name')
            # Look for custom type
            if 'type' not in self.get_args().keys():
                self.set_arg(parse_path.group(3), 'type')
                if self.get_arg('type') not in mh.__mediatypes__:
                    self.get_push().failure(
                        'Media type %s not recognized' %
                        self.get_arg('type'), True)
            logging.debug("Type detected: %s", self.get_arg('type'))
        else:
            logging.debug("No type detected")
            if self.get_setting('Deluge', 'enabled'):
                # Remove torrent
                import mediahandler.util.torrent as Torrent
                Torrent.remove_torrent(
                    self.get_setting('Deluge'),
                    self.get_arg('hash'))
            # Notify about failure
            self.get_push().failure(
                "No type or name specified for media: %s" %
                self.get_arg('name'), True)
        return

    # ======== HANDLE MEDIA ======== #

    def __handle_media(self):
        '''Sort args based on input'''
        logging.debug("Inputs: %s", self.args)
        # Determing if using deluge or not
        file_path = ''
        use_deluge = self.get_arg('use_deluge')
        if use_deluge:
            logging.info("Processing from deluge")
            file_path = path.join(self.get_arg('path'), self.get_args('name'))
        else:
            logging.info("Processing from command line")
            file_path = self.get_arg('media')
        # Parse directory structure
        self.__parse_dir(file_path)
        # Check that file was downloaded
        if path.exists(file_path):
            if self.get_setting('Deluge', 'enabled') and use_deluge:
                # Remove torrent
                import mediahandler.util.torrent as Torrent
                Torrent.remove_torrent(
                    self.get_setting('Deluge'),
                    self.get_arg('hash'))
            # Send to handler
            new_files = self.__file_handler(file_path)
            # Check that files were returned
            if new_files is None:
                self.get_push().failure("No media files found: %s" %
                                        self.get_arg('name'), True)
        else:
            # There was a problem, no files found
            self.get_push().failure("No media files found: %s" %
                                    self.get_arg('name'), True)
        return new_files

    # ======== MAIN ADD MEDIA FUNCTION ======== #

    def addmedia(self):
        '''Main function'''
        # Start main function
        new_files = self.__handle_media()
        # Exit
        return new_files
