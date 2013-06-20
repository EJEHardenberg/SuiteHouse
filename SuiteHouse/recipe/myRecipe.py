#Import google sign in
from google.appengine.api import users
from google.appengine.ext import db

from house import house
import recipe

import webapp2
import jinja2


#Import os for finding jinja
import os
import time

import logging


#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'])

class MyRecipes(webapp2.RequestHandler):

	def get(self):
		user = users.get_current_user()		

		if user:
			h = house.House.findHouseIDForUser(user.nickname())
			#Grab the user's recipes
			
			userRecipes = recipe.Recipe.getUserRecipes(user.nickname())

			
			template_values = {
				'username': user.nickname(),
				'recipes' : userRecipes
			}
			template = JINJA_ENVIRONMENT.get_template('myRecipe.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

	def post(self):

		try:
			user = users.get_current_user()

			if user:
				h = house.House.findHouseIDForUser(user.nickname())

				title = self.request.get('title')
				ingredients = self.request.get_all('ingredients[]')
				instructions = self.request.get_all('instructions[]')
				
				userRecipe = recipe.Recipe(title=title,instructions=instructions,ingredients=ingredients,house_id=h,associated_user=user.nickname())
				userRecipe.put()
				time.sleep(1)
				self.redirect('/recipe/myrecipes')

		except Exception, e:
			logging.error("Problem creating recipe ")
			logging.error(e)
			self.response.set_status(400,'Bad Request')
			self.redirect('/recipe/myrecipes')

		

