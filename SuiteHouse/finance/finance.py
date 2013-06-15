#Import google sign in
from google.appengine.api import users

import webapp2
import jinja2

#Import os for finding jinja
import os

import checkbook
import billTracker

#Make sure to setup the template rendering evironment in the templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'])

class FinancePage(webapp2.RequestHandler):

	def get(self):
		user = users.get_current_user()

		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		checkBookInfo = checkbook.CheckBook.getTotalIncomeAndExpense()

		template_values = {
			'username': user.nickname(),
			'cbIncome' : checkBookInfo['income'],
			'cbExpense' : checkBookInfo['expense'],
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/finance',FinancePage),
    ('/finance/',FinancePage),
    ('/finance/checkbook',checkbook.CheckBook),
    ('/finance/checkbook/',checkbook.CheckBook),
    ('/finance/billTracker',billTracker.BillTracker),
    ('/finance/billTracker/',billTracker.BillTracker),
], debug=True)
