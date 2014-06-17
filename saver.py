import webapp2
import jinja2
import os
import datetime
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

def two_digits(amount):
    #turn amount input into two digits amount
    if "." not in amount:
        return amount + ".00"
    else:
        dollar_cent = amount.split(".")
        cent = dollar_cent[1]
        if len(cent) > 2:
            return dollar_cent[0] + "." + dollar_cent[1][:2]
        elif len(cent) == 1:
            return dollar_cent[0] + "." + dollar_cent[1] + "0"
        elif len(cent) == 0:
            return dollar_cent[0] + "." + "00"

class UserPage(webapp2.RequestHandler):
    """ Handler for the front page after user login."""

    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('userhomepage.html')
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class Transaction(ndb.Model):
    # Models a transaction with description, tag, amount, date.
    user = ndb.UserProperty(auto_current_user_add=True)
    description = ndb.StringProperty()
    tag = ndb.StringProperty()
    amount = ndb.FloatProperty()
    date = ndb.DateProperty()

class TransactionSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the transaction added successful page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            #get the value from the transaction form
            amount = two_digits(self.request.get('amount'))
            description = self.request.get('description')
            tag = self.request.get('tag')
            date = self.request.get('date')
            
            #turn string date into a date variable
            year_month_day = date.split("-")
            year = int(year_month_day[0])
            month = int(year_month_day[1])
            day = int(year_month_day[2])
            date = datetime.date(year, month, day)
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'desc': description,
                'tag': tag,
                'amount': amount,
                'date': date
            }

            # construct Transaction object and store into database
            transaction = Transaction()
            transaction.description = description
            transaction.tag = tag
            transaction.amount = float(amount)
            transaction.date = date
            transaction.put()
            
            template = jinja_environment.get_template('transactionsuccessful.html')
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class Budgets(ndb.Model):
    # Models a budget which contain every tags' amount and period(monthly or yearly)
    user = ndb.UserProperty(auto_current_user_add=True)
    period = ndb.StringProperty()
    income = ndb.FloatProperty()
    food = ndb.FloatProperty()
    entertainment = ndb.FloatProperty()
    accommodation = ndb.FloatProperty()
    transport = ndb.FloatProperty()
    savings = ndb.FloatProperty()
    others = ndb.FloatProperty()

class BudgetSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the budget set successful page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            #get the value from transaction form
            period = self.request.get('setbudget').split(' ')[1]
            income = two_digits(self.request.get('income'))
            food = two_digits(self.request.get('food'))
            entertainment = two_digits(self.request.get('entertainment'))
            accommodation = two_digits(self.request.get('accommodation'))
            transport = two_digits(self.request.get('transport'))
            savings = two_digits(self.request.get('savings'))
            others = two_digits(self.request.get('others'))
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'period': period,
                'income': income,
                'food': food,
                'entertainment': entertainment,
                'accommodation': accommodation,
                'transport': transport,
                'savings': savings,
                'others': others
            }

            # construct Budgets object and store into database
            budgets = Budgets()
            budgets.period = period
            budgets.income = float(income)
            budgets.food = float(food)
            budgets.entertainment = float(entertainment)
            budgets.accommodation = float(accommodation)
            budgets.transport = float(transport)
            budgets.savings = float(savings)
            budgets.others = float(others)
            budgets.put()
            
            template = jinja_environment.get_template('budgetsuccessful.html')
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
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
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class LeaderboardPage(webapp2.RequestHandler):
    """ Handler for the leaderboard page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('leaderboard.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class WeeklyBestSaverPage(webapp2.RequestHandler):
    """ Handler for the weekly best saver page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('weeklybestsaver.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class YearlyBestSaverPage(webapp2.RequestHandler):
    """ Handler for the yearly best saver page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('yearlybestsaver.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class AboutPage(webapp2.RequestHandler):
    """ Handler for the about page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('about.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class TipsSharingFormPage(webapp2.RequestHandler):
    """ Handler for the tips sharing form page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('tipssharingform.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class TipsSharingPage(webapp2.RequestHandler):
    """ Handler for the tips sharing page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('tipssharing.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class SharingSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the tips sharing page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('tipssharingsuccessful.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class SharingPostPage(webapp2.RequestHandler):
    """ Handler for the tips sharing page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('tipssharingpost.html')
            self.response.out.write(template.render(template_values))
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
                               ('/chart', ChartViewPage),
                               ('/leaderboard', LeaderboardPage),
                               ('/weeklybestsaver', WeeklyBestSaverPage),
                               ('/yearlybestsaver', YearlyBestSaverPage),
                               ('/about', AboutPage),
                               ('/tipssharingform', TipsSharingFormPage),
                               ('/tipssharing', TipsSharingPage),
                               ('/sharingformsuccessful', SharingSuccessfulPage),
                               ('/sharingpost', SharingPostPage)],
                               debug=True)
