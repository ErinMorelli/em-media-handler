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
from mediahandler.util.args import get_arguments


# ======== DEFINE HANDLER CLASS ======== #

class Handler:
    '''Media handler class'''
    # ======== INIT CLASS ======== #

    def __init__(self):
        '''Initialize handler class'''
        # Set global variables
        self.args = {}
        self.settings = {}
        self.push = ''

    # ======== MOVE VIDEO FILES ======== #

    def add_video(self, src):
        '''Process video files'''
        logging.info("Moving file(s)")
        # Set which handler to use
        if self.args['type'] in ["TV", "Television", "TV Shows"]:
            (new_name, dst) = self.add_episode(src)
        elif self.args['type'] == 'Movies':
            (new_name, dst) = self.add_movie(src)
        # Check for errors
        if new_name is None:
            return None
        logging.debug("Name: %s", new_name)
        logging.debug("DST: %s", dst)
        # Check that new file exists
        if not path.isfile(dst):
            self.push.failure("File failed to move: %s" % self.args['name'])
        # Return new file name
        return new_name

    # ======== ADD TV EPISODE ======== #

    def add_episode(self, raw):
        '''Get and process TV episode information'''
        logging.info("Getting TV episode information")
        # Check that TV is enabled
        if not self.settings['TV']['enabled']:
            self.push.failure("TV type is not enabled")
        # Import TV module
        import mediahandler.types.tv as TV
        # Send info to handler
        (ep_title, new_file) = TV.get_episode(raw, self.settings['TV'])
        if ep_title is None:
            self.push.failure("Unable to match episode: %s"
                              % self.args['name'])
        # return folder and file paths
        return ep_title, new_file

    # ======== ADD MOVIE ======== #

    def add_movie(self, raw):
        '''Get and process movie information'''
        logging.info("Getting movie information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.push.failure("Movies type is not enabled")
        # Import movie module
        import mediahandler.types.movies as Movies
        # Send info to handler
        (mov_title, new_file) = Movies.get_movie(raw, self.settings['Movies'])
        if mov_title is None:
            self.push.failure("Unable to match movie: %s" % self.args['name'])
        # return folder and file paths
        return mov_title, new_file

    # ======== ADD MUSIC ======== #

    def add_music(self, raw, is_single=False):
        '''Get and process music information'''
        logging.info("Getting music information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.push.failure("Movies type is not enabled")
        # Import music module
        import mediahandler.types.music as Music
        # Send info to handler
        music_return = Music.get_music(raw, self.settings['Music'], is_single)
        (has_skips, music_info) = music_return
        # Check for no info
        if music_info is None:
            self.push.failure(
                "Unable to match music: %s" % self.args['name'])
        # Don't remove files if has skips
        if has_skips:
            self.settings['General']['keep_files'] = True
        # return album info
        return music_info

    # ======== ADD AUDIOBOOK ======== #

    def add_book(self, raw):
        '''Get and process book information'''
        logging.info("Getting audiobook information")
        # Check that Movies are enabled
        if not self.settings['Audiobooks']['enabled']:
            self.push.failure("Audiobooks type is not enabled")
        # Import audiobooks module
        import mediahandler.types.audiobooks as Audiobooks
        # Send to handler
        bok = Audiobooks.Book(self.settings['Audiobooks'])
        book_info = bok.get_book(raw, self.args['search'])
        logging.debug(book_info)
        if book_info is None:
            self.push.failure("Unable to match book: %s" % self.args['name'])
            return None
        # return book info
        return book_info

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
            return None
        # Send files back to handler
        return extracted

    # ======== SINGLE FILE HANDLER ======== #

    def __single_file(self, files):
        '''Process single files'''
        # Single file, treat differently
        logging.debug("Processing as a single file")
        self.settings['is_single'] = True
        # Look for zipped file first
        if search(r".(zip|rar|7z)$", files, I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.settings['has_filebot']:
                get_files = self.extract_files(files)
                # Check for failure
                if get_files is None:
                    return None
                # Rescan files
                self.__file_handler(get_files)
        # otherwise treat like other files
        if self.args['type'] == "Music":
            return self.add_music(files, True)
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
        self.settings['is_single'] = False
        # Get a list of files
        file_list = listdir(files)
        # Look for zipped file first
        if search(r".(zip|rar|7z)\n", '\n'.join(file_list), I):
            logging.debug("Zipped file type detected")
            # Send to extractor
            if self.settings['has_filebot']:
                get_files = self.extract_files(files)
                # Check for failure
                if get_files is None:
                    return None
                # Rescan files
                self.__file_handler(get_files)
        # Check for music
        if self.args['type'] == "Music":
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
        # Process books first
        if self.args['type'] == "Books" or self.args['type'] == "Audiobooks":
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
            self.push.failure("No %s files found for: %s"
                              % (self.args['type'], self.args['name']))
        # Remove old files
        if not self.settings['General']['keep_files']:
            if path.exists(files):
                if 'extracted' in self.settings.keys():
                    logging.debug("Removing extracted files folder")
                    rmtree(self.settings['extracted'])
                elif self.settings['is_single']:
                    logging.debug("Removing extra single file")
                    remove(files)
                else:
                    logging.debug("Removing extra files folder")
                    rmtree(files)
        # Send success notification
        self.push.success(added_files)
        # Finish
        return added_files

    # ======== PARSE DIRECTORY ======== #

    def __parse_dir(self, rawpath):
        '''Parse input directory structure'''
        logging.info("Extracing info from path")
        # Extract info from path
        parse_path = search(r"^((.*)?\/(.*))?\/(.*)$",
                            rawpath, I)
        if parse_path:
            self.args['path'] = parse_path.group(1)
            self.args['name'] = parse_path.group(4)
            # Look for custom type
            if 'type' not in self.args.keys():
                self.args['type'] = parse_path.group(3)
                if self.args['type'] not in mh.__mediatypes__:
                    self.push.failure(
                        'Media type %s not recognized' %
                        self.args['type'], True)
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
        return

    # ======== HANDLE MEDIA ======== #

    def __handle_media(self, use_deluge):
        '''Sort args based on input'''
        logging.debug("Inputs: %s", self.args)
        # Determing if using deluge or not
        media_dir = ''
        if use_deluge:
            logging.info("Processing from deluge")
            media_dir = self.args['path']
        else:
            logging.info("Processing from command line")
            media_dir = path.dirname(self.args['media'])
        # Check to see that files exist
        if not path.exists(media_dir):
            # There was a problem, no files found
            self.push.failure("No media files found: %s" % media_dir, True)
        # Parse directory structure
        self.__parse_dir(media_dir)
        # Check that file was downloaded
        file_path = self.args['path'] + "/" + self.args['name']
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

    def addmedia(self):
        '''Main function'''
        # Get arguments
        (use_deluge, self.args) = get_arguments()
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
        self.push = Notify.Push(self.settings['Pushover'], use_deluge)
        # Start main function
        new_files = self.__handle_media(use_deluge)
        # Exit
        return new_files
