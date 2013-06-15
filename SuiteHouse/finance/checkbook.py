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

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'],autoescape=True)


class CheckBookItem(db.Model):
	"""Model of a checkbook item"""
	description = db.StringProperty(indexed=False)
	date = db.DateProperty(auto_now_add=True)
	amount = db.FloatProperty(required=True)
	associated_user = db.StringProperty(required=True) #user_id of user

	@classmethod
	def by_id(cls,uid):
		c = CheckBookItem.all().filter('associated_user =',uid)
		return c


import logging

class CheckBook(webapp2.RequestHandler):

	@staticmethod
	def getTotalIncomeAnnExpense():
		"""Returns the total income and total expenses from the checkbook in a key value pair
			{'income' : x , 'expense' : y} 
		"""

		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			checkbook = CheckBookItem.by_id(user.nickname())

			#aggregate data
			runningIncome = 0
			runningExpense = 0

			for item in checkbook:
				if item.amount < 0:
					runningExpense = runningExpense + item.amount
				else:
					runningIncome = runningIncome + item.amount

			return {'income' : runningIncome, 'expense' : runningExpense}


		else:
			self.redirect(users.create_login_url(self.request.uri))

	def get(self):
		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			checkbook = CheckBookItem.by_id(user.nickname())

			template_values = {
				'username': user.nickname(),
				'items' : checkbook,
				'error' : self.request.get('err'),
			}

			template = JINJA_ENVIRONMENT.get_template('checkbook.html')
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
			self.redirect('/finance/checkbook?err=%s' % cgi.escape(err))

		postType = self.request.get('postType');

		if(postType == 'expense'):
			#If this has come from the expense form then we negate the value
			amount = 0 - amount
			

		#Create the new item and store it in the database
		if err == "":
			newItem = CheckBookItem(description=desc,amount=amount,associated_user=str(user.nickname()))
			newItem.put()
			time.sleep(1) # this is so that when we do the redirect (to essentially refresh the page), we ensure the datastore has been updated and we see a new value
			# we should redirect the user here, otherwise we ham up the redirects
			self.redirect('/finance/checkbook') #Probably want to pass some parameters to the url about success or not sucesss

	def delete(self):
		"""Respond to an http delete request, this will delete whatever CheckBookItem the request specifies"""

		#Get the key to the item
		body = json.loads((self.request.body))
		key = body['key']

		try:
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

				raise e

		
		



		
