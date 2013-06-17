#Database and user modeling libraries
from google.appengine.ext import db
from google.appengine.api import users

#Import logging library
import logging


class House(db.Model):
	"""	A House has many unqiue members, you can't join more than one house. If you do have to 'transfer'
		houses then there will be a system in place for it. A house is effectively a grouping on users
		and thats really about it.
	"""

	#Should figure out how to setup the ancestor query
	associated_users = db.StringProperty(required=True) #user_id's of user's
