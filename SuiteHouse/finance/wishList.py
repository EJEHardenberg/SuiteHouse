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


class WishListItem(baseItem.BaseItem,db.Model):
	"""Model of a checkbook item"""

	@classmethod
	def by_id(cls,uid):
		c = WishListItem.all().filter('associated_user =',uid)
		return c

class WishList(itemHandler.ItemHandler,webapp2.RequestHandler):
	wishes = []
	totalWishes = 0
	valuesRetrieved = False

	@staticmethod
	def getTotalBudgetExpense():
		"""Returns the total income and total expenses from the wishlist in a key value pair
			{'wishes' : x} 
		"""

		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			wishlist = WishListItem.by_id(user.nickname())

			#aggregate data
			runningExpense = 0

			for item in wishlist:
				runningExpense = runningExpense + item.amount
				

			return { 'wishes' : runningExpense}


		else:
			self.redirect(users.create_login_url(self.request.uri))

	def getStats(self):
		if self.valuesRetrieved:
			pass
		else:
			user = users.get_current_user()

			if user:
				items = WishListItem.by_id(user.nickname())
				for item in items:
					self.wishes.append(item)
					self.totalWishes += item.amount
				self.valuesRetrieved = True
			else:
				return None
		return {'wishes' : self.wishes, 'totalWishes' : self.totalWishes}

	def get(self):
		user = users.get_current_user()

		if user:
			#Get all the items associated with the user
			wishlist = WishListItem.by_id(user.nickname())

			template_values = {
				'username': user.nickname(),
				'items' : wishlist,
				'error' : self.request.get('err'),
			}

			template = JINJA_ENVIRONMENT.get_template('wishList.html')
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
			self.redirect('/finance/wishList?err=%s' % cgi.escape(err))

		postType = self.request.get('postType');

		if(postType == 'expense'):
			#If this has come from the expense form then we negate the value
			amount = 0 - amount
			

		#Create the new item and store it in the database
		if err == "":
			newItem = WishListItem(description=desc,amount=(0-amount),associated_user=str(user.nickname()))
			newItem.put()
			time.sleep(1) # this is so that when we do the redirect (to essentially refresh the page), we ensure the datastore has been updated and we see a new value
			# we should redirect the user here, otherwise we ham up the redirects
			self.redirect('/finance/wishList') #Probably want to pass some parameters to the url about success or not sucesss
