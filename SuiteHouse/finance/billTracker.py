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

	def delete(self):
		"""Respond to an http delete request, this will delete whatever BillItem the request specifies"""

		pass
			
	def put(self):
		pass

		
