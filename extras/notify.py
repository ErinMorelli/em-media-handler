#!/usr/bin/python
#
# This file is a part of EM Media Handler
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

import httplib, urllib, logging


# ======== PUSH CLASS DECLARTION ======== #

class Push:

	# ======== INIT NOTIFY CLASS ======== #

	def __init__(self, settings):
		logging.info("Initializing notification class")


	# ======== SEND MESSAGE VIA PUSHOVER ======== #

	def __sendMessage(self, message):
		logging.info("Sending push notification")
		# Initialize connection with pushover
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		# Encode request URL
		connUrl = urllib.urlencode({
			"token": settings['api_key'],
			"user": settings['user_key'],
			"title": "EM Media Handler",
			"message": message,
		})
		logging.debug("API call: %s", connUrl)
		# Send API request
		conn.request(
			"POST", 
			"/1/messages.json",
			connUrl, 
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
		# Get API response
		connResp = conn.getresponse()
		# Check for response success	
		if connResp != 200:
			logging.error("API Response: %s %s", connResp.status, connResp.reason)
		else:
			logging.info("API Response: %s %s", connResp.status, connResp.reason)
		logging.debug("After push notification send")


	# ======== SET SUCCESS INFO ======== #

	def Success(self, fileArray):
		logging.info("Starting success notifications")
		# Format file list
		mediaList = '\n    '.join(fileArray)
		# Send push notification
		logging.debug("Before push notification send")
		# Set success message
		connText = '''Media was successfully added to your server:
%s
		''' % mediaList
		# If push notifications enabled
		if settings['enabled']:
			# Send message
			self.__sendMessage(connText)


	# ======== SET ERROR INFO & EXIT ======== #

	def Failure(self, errorDetails):
		logging.info("Starting failure notifications")
		# Send push notification
		logging.debug("Before push notification send")
		# Set error message
		connText = '''There was an error reported:
%s
		''' % errorDetails
		# If push notifications enabled
		if settings['enabled']:
			# Send message
			self.__sendMessage(connText)
		# Raise python warning
		logging.warning(errorDetails)
		raise Warning(errorDetails)
