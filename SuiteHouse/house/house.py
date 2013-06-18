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
	associated_users = db.StringListProperty() #user_id's of user's

	@classmethod
	def findHouseByID(cls,house_id):
		u = House.all().get_by_id(house_id)
		return u

	@classmethod
	def findHouseIDForUser(cls,uid):
		u = House.all().filter('associated_users = ', uid).get()
		if u:
			return u.key().id()
		else:
			return -1

	def addMemberToHouse(cls,uid,house_id):
		#Is the user part of any other house?
		old = House.findHouseIDForUser(uid)
		if old:
			#Remove from house
			old.associated_users.remove(uid)
		newH = House.findHouseByID(house_id)
		if newH:
			newH.associated_users.append(uid)
		else:
			newH = House(associated_users=[uid])
		#Write.
		newH.put()
		return newH,key().id()

