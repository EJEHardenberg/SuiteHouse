#Import google sign in
from google.appengine.api import users
from google.appengine.ext import db


import webapp2
import jinja2


#Import os for finding jinja
import os

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'])

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

], debug=True)