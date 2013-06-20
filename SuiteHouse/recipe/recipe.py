#Import google sign in
from google.appengine.api import users
from google.appengine.ext import db

from house import house
import myRecipe

import webapp2
import jinja2


#Import os for finding jinja
import os

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'])

class Recipe(db.Model):
	"""
		Recipes are a list of ingredients, a user associated, a house associated, and instructions on how to make it
	"""
	title = db.StringProperty(required=True)
	instructions = db.StringListProperty()
	ingredients = db.StringListProperty()
	associated_user = db.StringProperty(required=True)
	house_id = db.IntegerProperty(required=True)

	@classmethod
	def getHouseRecipes(cls,house_id):
		c = Recipe.all().filter('house_id =',house_id)
		return c

	@classmethod
	def getHouseRecipeForUser(cls,house_id,associated_user):
		c = Recipe.all().filter('house_id = ', house_id).filter('associated_user =',  associated_user)
		return c

	@classmethod
	def getUserRecipes(cls,associated_user):
		c = Recipe.all().filter('associated_user = ', associated_user)
		return c


class RecipeHandler(webapp2.RequestHandler):

	def get(self):
		user = users.get_current_user()

		if user:
			#Store the user information if they don't exist already 

			template_values = {
				'username': user.nickname(),
			}
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

		

application = webapp2.WSGIApplication([
    ('/recipe', RecipeHandler),
    ('/recipe/', RecipeHandler),
    ('/recipe/myrecipes',myRecipe.MyRecipes),
    ('/recipe/myrecipes/',myRecipe.MyRecipes),

], debug=True)