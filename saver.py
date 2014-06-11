import webapp2
import jinja2
import os

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class UserPage(webapp2.RequestHandler):
    """ Handler for the front page after user login."""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('userhomepage.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class ManagePage(webapp2.RequestHandler):
    """ Handler for the manage page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('manage.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class TransactionPage(webapp2.RequestHandler):
    """ Handler for the add new transaction page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('transaction.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class TransactionSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the transaction added successful page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('transactionsuccessful.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class MonthlyBudgetPage(webapp2.RequestHandler):
    """ Handler for monthly budget page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('monthlybudget.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class YearlyBudgetPage(webapp2.RequestHandler):
    """ Handler for yearly budget page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('yearlybudget.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class BudgetSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the budget set successful page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('budgetsuccessful.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class OverviewPage(webapp2.RequestHandler):
    """ Handler for the transaction successful page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('overview.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class SummaryPage(webapp2.RequestHandler):
    """ Handler for the transaction successful page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('summary.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class TransactionHistoryPage(webapp2.RequestHandler):
    """ Handler for the transaction history page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('transactionhistory.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)

class ChartViewPage(webapp2.RequestHandler):
    """ Handler for the chart view page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('chartview.html')
            self.response.out.write(template.render())
        else:
            self.redirect(self.request.host_url)



app = webapp2.WSGIApplication([('/user', UserPage),
                               ('/manage', ManagePage),
                               ('/transaction', TransactionPage),
                               ('/transuccessful', TransactionSuccessfulPage),
                               ('/monthlybudget', MonthlyBudgetPage),
                               ('/yearlybudget', YearlyBudgetPage),
                               ('/budgetsuccessful', BudgetSuccessfulPage),
                               ('/overview', OverviewPage),
                               ('/summary', SummaryPage),
                               ('/history', TransactionHistoryPage),
                               ('/chart', ChartViewPage)],
                               debug=True)
