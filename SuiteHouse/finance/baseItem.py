from google.appengine.ext import db



class BaseItem(db.Model):
	"""Base class for all items, handles fields in common with CheckBookItems, WishList Items, and BillItems"""
	description = db.StringProperty(indexed=False)
	date = db.DateProperty(auto_now_add=True)
	amount = db.FloatProperty(required=True)
	associated_user = db.StringProperty(required=True) #user_id of user