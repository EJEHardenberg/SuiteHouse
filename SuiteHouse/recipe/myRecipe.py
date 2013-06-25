#Import google sign in
from google.appengine.api import users
from google.appengine.ext import db

from house import house
import recipe

import webapp2
import jinja2
import json

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

		try:
			#If there's a key then that means we're responding to an ajax request and should send back json of the recipe
			key = self.request.get('key')

			requestedRecipe = db.get(db.Key(encoded=str(key)))
			self.response.set_status(200,json.dumps({'key' : key, 
													 'title' : requestedRecipe.title, 
													 'ingredients' : requestedRecipe.ingredients,
													 'instructions': requestedRecipe.instructions,
													 'rank' : requestedRecipe.rank
													 }))
			self.response.write(json.dumps({'key' : key, 
													 'title' : requestedRecipe.title, 
													 'ingredients' : requestedRecipe.ingredients,
													 'instructions': requestedRecipe.instructions,
													 'rank': requestedRecipe.rank
													 }))
			
		except Exception, e:
			logging.info(e)
			#handle the errorful key
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
				
				userRecipe = recipe.Recipe(title=title,instructions=instructions,ingredients=ingredients,house_id=h,associated_user=user.nickname(),rank=0)
				userRecipe.put()
				time.sleep(1)
				self.redirect('/recipe/myrecipes')

		except Exception, e:
			logging.error("Problem creating recipe ")
			logging.error(e)
			self.response.set_status(400,'Bad Request')
			self.redirect('/recipe/myrecipes')

	def delete(self):
		"""Respond to an http delete request, this will delete whatever Item the request specifies"""
		#Get the key to the item
		try:
			key = self.request.get("key")
			item = db.get(db.Key(encoded=str(key)))
			item.delete()
			self.response.set_status(200,json.dumps({'key' : key}))
			self.response.write(key)
		except Exception, e:
			self.response.set_status(404,json.dumps({'key' : 'Not found'}))
			logging.error(e)
		else:
			pass

	def put(self):
		"""Respond to an http put request and update a given recipe""" 
		try:

			information = json.loads(str(self.request.body))
			key = information['key']
			newTitle = information['title']
			newIngredients = information['ingredients']
			newInstructions = information['instructions']

			item = db.get(db.Key(encoded=str(key)))

			item.title = newTitle
			item.ingredients = newIngredients
			item.instructions = newInstructions

			item.put()
			time.sleep(1)
			self.response.out.set_status(200,'Resource Updated')
			self.response.out.write('Resource Updated')
		

		except Exception, e:
			self.response.set_status(404,json.dumps({'message' : e}))
			logging.error(e)
		
		self.response.out.set_status(200,'Resource Updated')
		self.response.out.write('200')

