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
import itemHandler

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'],autoescape=True)


class CheckBookItem(baseItem.BaseItem,db.Model):
	"""Model of a checkbook item"""
	date = db.DateProperty(auto_now_add=True)

	@classmethod
	def by_id(cls,uid):
		c = CheckBookItem.all().filter('associated_user =',uid)
		return c

	@classmethod
	def by_id_forMonth(cls,uid):
		month = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		c = CheckBookItem.all().filter('associated_user =',uid).filter('date >= ',month)
		return c

class CheckBook(itemHandler.ItemHandler,webapp2.RequestHandler):
	valuesRetrieved = False
	incomes = []
	expenses = []
	totalIncome = 0
	totalExpense = 0

	def getStats(self):
		if self.valuesRetrieved:
			pass
		else:
			self.incomes = []
			self.expenses = []
			self.totalExpense = 0
			self.totalExpense = 0
			#Get everything for this month
			user = users.get_current_user()
			if user:
				items = CheckBookItem.by_id_forMonth(user.nickname())
				self.totalExpense = 0
				self.totalIncome = 0
				for item in items:
					if item.amount < 0:
						self.expenses.append(item)
						self.totalExpense += item.amount
					else:
						self.incomes.append(item)
						self.totalIncome += item.amount
				self.valuesRetrieved = True
			else:
				#No can do
				return None
		return {'incomes' : self.incomes, 'expenses' : self.expenses, 'totalIncome' : self.totalIncome, 'totalExpense' : self.totalExpense}


	@staticmethod
	def getTotalIncomeAndExpense():
		"""Returns the total income and total expenses from the checkbook in a key value pair
			{'income' : x , 'expense' : y} 
		"""

		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			checkbook = CheckBookItem.by_id_forMonth(user.nickname())

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
