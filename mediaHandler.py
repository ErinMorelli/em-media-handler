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


# ======== IMPORT MODULES ======== #

import sys, re
import shutil, logging

from os import path, listdir, makedirs
from twisted.internet import reactor
from deluge.ui.client import client
from deluge.log import setupLogger

import media.tv, media.movies, media.music, media.audiobooks
import notify.email, notify.pushover
import extras.extract, config


# ======== SET GLOBAL HANDLER OPTIONS ======== #

handler = {
	'rmFiles': False,
	'logging': {
		'file': 'logs/handler.log', # Path to debugging log
		'level': logging.DEBUG, # default: error (debug, info, warning, error, critical)
	}, 
	'deluge': {
		'host': '127.0.0.1',
		'port': 58846,
		'username': 'deluge',
		'password': 'deluge'
	},
}


# ======== NOTIFY ======== #

def Success(msg):
	logging.info("Notifying successful")
	n = notify.Notification(msg)
	n.notifySuccess()
	return

def Failure(msg):
	logging.error(msg)
	logging.info("Notifying failure")
	n = notify.Notification(msg)
	n.notifyFailure()
	return

# ======== MOVE ANY FILE ======== #

def move_file(src):
	logging.info("Moving file(s)")
	# Set metadata options
	metadata = {
		"TV" : get_episode_info,
		"Movies" : get_movie_info,
	}
	# Get paths
	fileinfo = metadata[ttype](src) 
	# Check for errors
	if fileinfo == None:
		return None
	# Extract info
	(new_name, dst) = fileinfo
	logging.debug("Name: %s", new_name)
	logging.debug("DST: %s", dst)
	# Check that new file exists
	if not path.isfile(dst):
		Failure("File failed to move %s" % dst)
		return None
	# Return destination path
	return dst, new_name


# ======== TELEVISION ======== #

# GET EPISODE INFO
def get_episode_info(raw):
	logging.info("Getting TV episode information")
	# Send info to handler
	r = naming.Rename(raw)
	epInfo = r.episodeHandler()
	if epInfo == None:
		Failure("Unable to match episode: %s" % raw)
		return None
	# Extract info
	(ep_title, new_file) = epInfo
	# return folder and file paths
	return ep_title, new_file


# ======== MOVIES ======== #

# GET MOVIE INFO
def get_movie_info(raw):
	logging.info("Getting movie information")
	# Send info to handler
	r = naming.Rename(raw)
	movInfo = r.movieHandler()
	if movInfo == None:
		Failure("Unable to match movie: %s" % raw)
		return None
	# Extract info
	(mov_title, new_file) = movInfo
	# return folder and file paths
	return mov_title, new_file


# ======== MUSIC ======== #

# ADD MUSIC TO COLLETION
def add_music(raw, isSingle=False):
	logging.info("Getting music information")
	r = naming.Rename(raw)
	(err, musicInfo) = r.musicHandler(isSingle)
	if err:
		Failure("Unable to match music: %s\n%s" % (raw, musicInfo))
		return None
	# return album info
	return musicInfo


# ======== AUDIOBOOKS ======== #

# GET BOOK INFO
def add_book(raw):
	logging.info("Getting audiobook information")
	b = audiobooks.Book()
	bookInfo = b.getBook(raw)
	if bookInfo == None:
		Failure("Unable to match book: %s\n%s" % raw, bookInfo)
		return None
	# return book info
	return bookInfo


# ======== EXTRACTION FUNCTION ======== #

def extract_files(raw):
	logging.info("Extracting files from compressed file")
	# Send info to handler
	e = naming.Extract(file)
	extracted = e.fileHandler()
	if extracted == None:
		Failure("Unable to extract files: %s" % raw)
		return None
	# Send files back to handler
	return extracted


# ======== MAIN FILE FUNCTION ======== #

def file_handler(files):
	logging.info("Starting files handler")
	added_files = []
	# Process books first
	if ttype == "Books":
		added_file = add_book(files)
		added_files.append(added_file)
	# Then check for folders/files
	elif path.isfile(files):
		# Single file, treat differently
		logging.debug("Proecessing as a single file")
		# Look for zipped file first
		if re.search(r".(zip|rar|7z)$", files, re.I):
			logging.debug("Zipped file type detected")
			# Send to extractor
			get_files = extract_files(src)
			# Check for failure
			if get_files == None:
				return None
			# Rescan files
			file_handler(get_files)
		# otherwise treat like other files
		if ttype == "Music":
			added_file = add_music(files, True)
			added_files.append(added_file)
		else: 
			# Set single file as source
			src = files
			# Move file
			moveinfo = move_file(src)
			# Check for problems 
			if moveinfo == None:
				return
			(dst, added_file) = moveinfo
			added_files.append(added_file)
	else:
		# Otherwise process as folder
		logging.debug("Proecessing as a folder")
		if ttype == "Music":
			added_file = add_music(files)
			added_files.append(added_file)
		else: 
			# Get a list of files
			file_list = listdir(files)
			# Locate video file in folder
			for f in file_list:
				# Look for file types we want
				if re.search(r"\.(mkv|avi|m4v|mp4)$", f, re.I):
					# Set info
					filename = f
					src = files+'/'+filename
					# Move file
					moveinfo = move_file(src)
					# Check for problems 
					if moveinfo == None:
						return
					(dst, added_file) = moveinfo
					added_files.append(added_file)
	# Remove old files
	if handler['rmFiles']:
		if path.exists(files):
			logging.debug("Removing extra files")
			shutil.rmtree(files)
	# Send notification
	Success(added_files)
	# Finish
	return


# ======== REMOVE TORRENT ======== #

def remove_torrent():
	logging.info("Removing torrent from Deluge")
	# Connect to Deluge daemon
	d = client.connect(
		host = handler['deluge']['host'],
		port = handler['deluge']['port'],
		username = handler['deluge']['username'],
		password = handler['deluge']['password']
	)
	# We create a callback function to be called upon a successful connection
	def on_connect_success(result):
		logging.debug("Connection was successful!")
		def on_remove_torrent(success):
			if success:
				logging.debug("Remove successful: %s", tname)
			else:
				logging.warning("Remove unsuccessful: %s", tname)
			# Disconnect from the daemon & exit
			client.disconnect()
			reactor.stop()
		def on_get_session_state(torrents):
			found = False
			# Look for completed torrent in list
			for t in torrents:
				if t == thash:
					# Set as found and call remove function
					logging.debug("Torrent found: %s", tname)
					found = True
					client.core.remove_torrent(thash, False).addCallback(on_remove_torrent)
					break
			if not found:
				logging.warning("Torrent not found: %s", tname)
				# Disconnect from the daemon & exit
				client.disconnect()
				reactor.stop()
		# Get list of current torrent hashes
		client.core.get_session_state().addCallback(on_get_session_state)
	# We add the callback to the Deferred object we got from connect()
	d.addCallback(on_connect_success)
	# We create another callback function to be called when an error is encountered
	def on_connect_fail(result):
		logging.error("Connection failed: %s", result)
	# We add the callback (in this case it's an errback, for error)
	d.addErrback(on_connect_fail)
	# Run the twisted main loop to make everything go
	reactor.run()


# ======== MAIN FUNCTION WRAPPER ======== #

def main():
	logging.info("Starting main function")
	# Get arguments from Deluge
	global thash, tname, tpath
	thash = sys.argv[1]
	tname = sys.argv[2]
	tpath = sys.argv[3]
	logging.critical("Processing: %s", tname)
	logging.debug("Inputs: %s, %s, %s", thash, tname, tpath)
	# Extract media type from path
	global ttype
	find_type = re.search(r"^\/([a-z]+)$", tpath, re.I)
	if find_type and find_type.group(1):
		ttype = find_type.group(1)
		logging.debug("Type detected: %s", ttype)
	else:
		# Remove torrent
		remove_torrent()
		# Notify about failure
		Failure("No type specified for download: %s" % tname)
		return
	# Check that file was downloaded
	files = tpath+"/"+tname
	if path.exists(files):
		# Remove torrent
		remove_torrent()
		# Send to handler
		file_handler(files)
	else:
		# There was a problem, no files found
		Failure("No downloaded files found: %s" % tname)
	return


# ======== LOGGING ======== #

def init_logging():
	logging.basicConfig(
		filename=handler['logging']['file'],
		format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
		level=handler['logging']['level'],
	)
	setupLogger()
	return


# ======== RUN THINGS ======== #

# If this is commandline, get args & run
if __name__=='__main__':
	init_logging()
    	main()
