#Import google sign in
from google.appengine.api import users
from google.appengine.ext import db

from house import house
import recipe

import webapp2
import jinja2


#Import os for finding jinja
import os

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
		logging.info(self.request.body)

		

