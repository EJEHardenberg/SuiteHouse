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

	def get(self):
		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			checkbook = CheckBookItem.by_id(user.nickname())

			template_values = {
				'username': user.nickname(),
				'items' : checkbook			
			}

			template = JINJA_ENVIRONMENT.get_template('checkbook.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def post(self):
		user = users.get_current_user()
		desc = cgi.escape(self.request.get('description'))
		amount = float(cgi.escape(self.request.get('amount')))
		postType = self.request.get('postType');

		if(postType == 'expense'):
			#If this has come from the expense form then we negate the value
			amount = 0 - amount

		#Create the new item and store it in the database
		newItem = CheckBookItem(description=desc,amount=amount,associated_user=str(user.nickname()))
		newItem.put()

		#redirect the user to the proper page

		self.redirect('/finance/checkbook') #Probably want to pass some parameters to the url about success or not sucesss

	def delete(self):
		"""Respond to an http delete request, this will delete whatever CheckBookItem the request specifies"""

		#Get the key to the item
		body = json.loads((self.request.body))
		key = body['key']

		item = db.get(db.Key(encoded=str(key)))
		item.delete()
		self.response.set_status(200,json.dumps({'key' : key}))
		self.response.write(key)
		



		
