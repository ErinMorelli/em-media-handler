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
from os import path, listdir
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

    def __add_video(self, src):
        '''Process video files'''
        logging.info("Moving file(s)")
        file_info = None
        # Set which handler to use
        if self.args['type'] in ["TV", "Television", "TV Shows"]:
            file_info = self.__add_episode(src)
        elif self.args['type'] == 'Movies':
            file_info = self.__add_movie(src)
        # Check for errors
        if file_info is None:
            return None
        # Extract info
        (new_name, dst) = file_info
        logging.debug("Name: %s", new_name)
        logging.debug("DST: %s", dst)
        # Check that new file exists
        if not path.isfile(dst):
            self.push.failure("File failed to move: %s" % self.args['name'])
        # Return new file name
        return new_name

    # ======== ADD TV EPISODE ======== #

    def __add_episode(self, raw):
        '''Get and process TV episode information'''
        logging.info("Getting TV episode information")
        # Check that TV is enabled
        if not self.settings['TV']['enabled']:
            self.push.failure("TV type is not enabled")
        # Import TV module
        import mediahandler.types.tv as TV
        # Send info to handler
        epi = TV.Episode(self.settings['TV'])
        ep_info = epi.get_episode(raw)
        if ep_info is None:
            self.push.failure("Unable to match episode: %s"
                              % self.args['name'])
        # Extract info
        (ep_title, new_file) = ep_info
        # return folder and file paths
        return ep_title, new_file

    # ======== ADD MOVIE ======== #

    def __add_movie(self, raw):
        '''Get and process movie information'''
        logging.info("Getting movie information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.push.failure("Movies type is not enabled")
        # Import movie module
        import mediahandler.types.movies as Movies
        # Send info to handler
        mov = Movies.Movie(self.settings['Movies'])
        mov_info = mov.get_movie(raw)
        if mov_info is None:
            self.push.failure("Unable to match movie: %s" % self.args['name'])
        # Extract info
        (mov_title, new_file) = mov_info
        # return folder and file paths
        return mov_title, new_file

    # ======== ADD MUSIC ======== #

    def __add_music(self, raw, is_single=False):
        '''Get and process music information'''
        logging.info("Getting music information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.push.failure("Movies type is not enabled")
        # Import music module
        import mediahandler.types.music as new_music
        # Send info to handler
        mus = new_music.Music(self.settings['Music'])
        music_info = mus.add_music(raw, is_single)
        if music_info is None:
            self.push.failure(
                "Unable to match music: %s" % self.args['name'])
        # return album info
        return music_info

    # ======== ADD AUDIOBOOK ======== #

    def __add_book(self, raw):
        '''Get and process book information'''
        logging.info("Getting audiobook information")
        # Check that Movies are enabled
        if not self.settings['Audiobooks']['enabled']:
            self.push.failure("Audiobooks type is not enabled")
        # Import audiobooks module
        import mediahandler.types.audiobooks as Audiobooks
        # Send to handler
        bok = Audiobooks.Book(self.settings['Audiobooks'])
        book_info = bok.get_book(raw)
        if book_info is None:
            self.push.failure("Unable to match book: %s" % self.args['name'])
            return None
        # return book info
        return book_info

    # ======== EXTRACT FILES ======== #

    def __extract_files(self, raw):
        '''Send files to be extracted'''
        logging.info("Extracting files from compressed file")
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

    # ======== MAIN FILE HANDLER ======== #

    def __file_handler(self, files):
        '''Handle files by type'''
        logging.info("Starting files handler")
        added_files = []
        # Process books first
        if self.args['type'] == "Books" or self.args['type'] == "Audiobooks":
            added_file = self.__add_book(files)
            added_files.append(added_file)
        # Then check for folders/files
        elif path.isfile(files):
            # Single file, treat differently
            logging.debug("Processing as a single file")
            # Look for zipped file first
            if search(r".(zip|rar|7z)$", files, I):
                logging.debug("Zipped file type detected")
                # Send to extractor
                if (self.settings['TV']['enabled'] or
                   self.settings['Movies']['enabled']):
                    get_files = self.__extract_files(files)
                    # Check for failure
                    if get_files is None:
                        return None
                    # Rescan files
                    self.__file_handler(get_files)
            # otherwise treat like other files
            if self.args['type'] == "Music":
                added_file = self.__add_music(files, True)
                added_files.append(added_file)
            else:
                # Set single file as source
                src = files
                # Move file
                video_info = self.__add_video(src)
                # Check for problems
                if video_info is None:
                    return
                added_file = video_info
                added_files.append(added_file)
        else:
            # Otherwise process as folder
            logging.debug("Proecessing as a folder")
            if self.args['type'] == "Music":
                added_file = self.__add_music(files)
                added_files.append(added_file)
            else:
                # Get a list of files
                file_list = listdir(files)
                # Locate video file in folder
                for item in file_list:
                    # Look for file types we want
                    if search(r"\.(mkv|avi|m4v|mp4)$", item, I):
                        # Set info
                        file_name = item
                        src = files+'/'+file_name
                        # Move file
                        video_info = self.__add_video(src)
                        # Check for problems
                        if video_info is None:
                            return
                        added_file = video_info
                        added_files.append(added_file)
        # Remove old files
        if not self.settings['General']['keep_files']:
            if path.exists(files):
                logging.debug("Removing extra files")
                rmtree(files)
        # Send success notification
        self.push.success(added_files)
        # Finish
        return added_files

    # ======== HANDLE MEDIA ======== #

    def __handle_media(self, use_deluge):
        '''Sort args based on input'''
        logging.debug("Inputs: %s", self.args)
        # Determing if using deluge or not
        if use_deluge:
            logging.info("Processing from deluge")
            # Make sure path exists
            if not path.exists(self.args['path']):
                # There was a problem, no files found
                self.push.failure("No media files found: %s"
                                  % self.args['name'])
            # Extract media type from path
            find_type = search(r"^(.*)?\/(.*)$", self.args['path'], I)
            if find_type:
                self.args['type'] = find_type.group(2)
                # Check is valid type
                if self.args['type'] not in mh.typeslist:
                    self.push.failure(
                        'Media type %s not recognized' % self.args['type'])
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
                    "No type specified for download: %s" % self.args['name'])
        else:
            logging.info("Processing from command line")
            # Make sure path exists
            media_dir = path.dirname(self.args['media'])
            if not path.exists(media_dir):
                # There was a problem, no files found
                self.push.failure("No media files found: %s"
                                  % self.args['name'])
            # Extract info from path
            parse_path = search(r"^((.*)?\/(.*))\/(.*)$",
                                media_dir, I)
            if parse_path:
                self.args['path'] = parse_path.group(1)
                self.args['name'] = parse_path.group(4)
                # Look for custom type
                if 'type' not in self.args.keys():
                    self.args['type'] = parse_path.group(3)
                    if self.args['type'] not in mh.typeslist:
                        self.push.failure(
                            'Media type %s not recognized' %
                            self.args['type'])
                logging.debug("Type detected: %s", self.args['type'])
            else:
                logging.debug("No type detected")
                # Notify about failure
                self.push.failure(
                    "No type or name specified for media: %s" %
                    self.args['name'])
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
        else:
            # There was a problem, no files found
            self.push.failure("No media files found: %s" % self.args['name'])
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
        self.push = Notify.Push(self.settings['Pushover'])
        # Start main function
        new_files = self.__handle_media(use_deluge)
        # Exit
        return new_files
