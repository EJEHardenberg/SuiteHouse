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


import baseItem

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'],autoescape=True)


class BillItem(baseItem.BaseItem,db.Model):
	"""Model of a fixed expense item"""

	@classmethod
	def by_id(cls,uid):
		c = BillItem.all().filter('associated_user =',uid)
		return c

	@classmethod
	def by_id_forMonth(cls,uid):
		month = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		c = BillItem.all().filter('associated_user =',uid).filter('date >= ',month)
		return c


import logging

class BillTracker(webapp2.RequestHandler):
	@staticmethod
	def getTotalBills():
		"""Returns the total bill expenses from the database in a key value pair
			{'bills' : x } 
		"""

		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			bills = BillItem.by_id_forMonth(user.nickname())

			#aggregate data
			runningBills = 0

			for item in bills:
				runningBills = runningBills + item.amount

			return {'bills' : runningBills}


		else:
			self.redirect(users.create_login_url(self.request.uri))

	def get(self):
		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			bills = BillItem.by_id(user.nickname())

			template_values = {
				'username': user.nickname(),
				'items' : bills,
				'error' : self.request.get('err'),
			}

			template = JINJA_ENVIRONMENT.get_template('billTracker.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def post(self):
		user = users.get_current_user()
		desc = cgi.escape(self.request.get('description'))
		amount = cgi.escape(self.request.get('amount'))
		err = ""
		
		try:
			amount = float(amount)
		except Exception, e:
			#They didn't submit a numeric integer (aka they just hit submit without entering a value)
			err = "Please enter an amount for your item"
			amount = 0
			#Redirects here don't work for some reason
			self.response.set_status(400,'Bad amount value')
			self.response.write(err)
			self.redirect('/finance/billTracker?err=%s' % cgi.escape(err))

		#We negate the value because we don't except negative values in the html input form
		amount = 0 - amount
			

		#Create the new item and store it in the database
		if err == "":
			newItem = BillItem(description=desc,amount=amount,associated_user=str(user.nickname()))
			newItem.put()
			time.sleep(1) # this is so that when we do the redirect (to essentially refresh the page), we ensure the datastore has been updated and we see a new value
			# we should redirect the user here, otherwise we ham up the redirects
			self.redirect('/finance/billTracker') 

	def delete(self):
		"""Respond to an http delete request, this will delete whatever BillItem the request specifies"""

		#TODO: Since we use the database key, we could probably just abstract this method to a higher class for each controller

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

		
