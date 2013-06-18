#Import google sign in
from google.appengine.api import users

#database modeling
from google.appengine.ext import db

import webapp2
import jinja2

#Import os for finding jinja
import os

#Import escaping and data parsing tools
import json
import cgi

#Import logging library
import logging

#Import time library
import time
import datetime

class ItemHandler(webapp2.RequestHandler):

	def delete(self):
		"""Respond to an http delete request, this will delete whatever Item the request specifies"""
		#Get the key to the item
		try:
			body = json.loads((self.request.body))
			key = body['key']
			item = db.get(db.Key(encoded=str(key)))
			item.delete()
			self.response.set_status(200,json.dumps({'key' : key}))
			self.response.write(key)
		except Exception, e:
			self.response.set_status(404,json.dumps({'key' : 'Not found'}))
			logging.error(e)
		else:
			#Carry on my wayward (son
			pass
			
	def put(self):
		#Since this retrieves via key, we could probably abstract a good portion of it out to a controller class... 
		body = json.loads(self.request.body)
		key = body['key']

		amount = None
		description = None

		try:
			amount = body['amount']
		except Exception, e:
			#no amount to have
			pass

		try:
			description = body['description']
		except Exception, e:
			#no description to have
			pass

		#Did they submit something worthwhile?
		if amount or description:
			try:
				item = db.get(db.Key(encoded=str(key)))
				if amount:
					item.amount = float(amount)
				if description:
					item.description = description
				item.put()
				self.response.set_status(200,json.dumps({'key' : key}))
				self.response.write(key)
			except Exception, e:
				logging.info(e)
				self.response.set_status(500,json.dumps({'error' : str(e)}))
				self.response.write('Could not complete update')

		
