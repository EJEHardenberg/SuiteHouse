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

#import submodules to get data
import checkbook
import billTracker
import wishList

import knapsack

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'],autoescape=True)


class Budget(webapp2.RequestHandler):

	def get(self):
		user = users.get_current_user()

		if user:

			template_values = {
				'username': user.nickname(),
				'error' : self.request.get('err'),
			}

			template = JINJA_ENVIRONMENT.get_template('budget.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def post(self):
		#This will be the calculate method

		#Everything must be done through the user id
		user = users.get_current_user()

		if user:
			#Get the total income and calculate the expenses
			cb = checkbook.CheckBook()
			cbInfo = cb.getStats()

			#Get the bills
			bt = billTracker.BillTracker()
			btInfo = bt.getStats()

			#Get wishlist
			wl = wishList.WishList()
			wlInfo = wl.getStats()

			#First knap sack
			limit = cbInfo['totalIncome'] - btInfo['totalBills']
			#If we can't even afford our fixed bills, we're having a bad time.
			if limit <= 0:
				pass
			else:
				#Solve the knapsack problem using the limit and the expenses
				k = knapsack.Knapsack(round(abs(limit)+.5),cbInfo['expenses'])
				results = k.solve()
				logging.info(results)

		else:
			self.redirect(users.create_login_url(self.request.uri))

		
