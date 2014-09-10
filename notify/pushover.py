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

from smtplib import SMTP
import datetime, base64
import httplib, urllib, logging


# ======== CLASS DECLARTION ======== #

class Notification:
	def __init__(self, filearray):
		logging.info("Initializing notification class")
		self.files = filearray

	def notifySuccess(self):
		logging.info("Starting success notifications")

		# Send push notification
		logging.debug("Before push notification send")
		conn = httplib.HTTPSConnection("api.pushover.net:443")

		conn_text = '''Media was successfully added to your server:
%s
		''' % media_list

		conn_url = urllib.urlencode({
			"token": "",
			"user": "",
			"title": "EM Media Handler",
			"message": conn_text,
		})
		logging.debug("API call: %s", conn_url)

		conn.request(
			"POST", 
			"/1/messages.json",
			conn_url, 
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
		conn_resp = conn.getresponse()
		if conn_resp != 200:
			logging.error("API Response: %s %s", conn_resp.status, conn_resp.reason)
		else:
			logging.info("API Response: %s %s", conn_resp.status, conn_resp.reason)

		logging.debug("After push notification send")


	def notifyFailure(self):
		logging.info("Starting failure notifications")

		# Send push notification
		logging.debug("Before push notification send")
		conn = httplib.HTTPSConnection("api.pushover.net:443")

		conn_text = '''There was an error reported:
%s
		''' % self.files

		conn_url = urllib.urlencode({
			"token": "",
			"user": "",
			"title": "EM Media Handler",
			"message": conn_text,
		})
		logging.debug("API call: %s", conn_url)

		conn.request(
			"POST", 
			"/1/messages.json",
			conn_url, 
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
		conn_resp = conn.getresponse()
		if conn_resp != 200:
			logging.error("API Response: %s %s", conn_resp.status, conn_resp.reason)
		else:
			logging.info("API Response: %s %s", conn_resp.status, conn_resp.reason)

		logging.debug("After push notification send")
