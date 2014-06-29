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

    #remove extra "0" in the amount variable
    amount = float(amount)
    amount = str(amount)

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
        else:
            return amount

class UserSummary(ndb.Model):
    # Models a summary of user's total expenses, budgets, incomes, savings etc
    user = ndb.UserProperty(auto_current_user_add=True)
    month = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    total_income = ndb.StringProperty()
    total_savings = ndb.StringProperty()
    total_budget = ndb.StringProperty()
    total_expenses = ndb.StringProperty()
    total_food_expenses = ndb.StringProperty()
    total_entertainment_expenses = ndb.StringProperty()
    total_accommodation_expenses = ndb.StringProperty()
    total_transport_expenses = ndb.StringProperty()
    total_savings_expenses = ndb.StringProperty()
    total_others_expenses = ndb.StringProperty()
    budget_available = ndb.StringProperty()

    def initialization(self): #initialize all variable to "0.00"
        self.month = datetime.datetime.now().month
        self.year = datetime.datetime.now().year
        self.total_income = "0.00"
        self.total_savings = "0.00"
        self.total_budget = "0.00"
        self.total_expenses = "0.00"
        self.total_food_expenses = "0.00"
        self.total_entertainment_expenses = "0.00"
        self.total_accommodation_expenses = "0.00"
        self.total_transport_expenses = "0.00"
        self.total_savings_expenses = "0.00"
        self.total_others_expenses = "0.00"
        self.budget_available = "0.00"

class UserPage(webapp2.RequestHandler):
    """ Handler for the front page after user login."""

    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            summary = UserSummary.query(UserSummary.user == user).fetch()

            # initialize value of total_expenses and budget_available and retrieve if exists
            total_expenses = '0.00'
            budget_available = '0.00'
            if len(summary) == 1: #does contain user summary
                total_expenses = summary[0].total_expenses
                budget_available = summary[0].budget_available
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'total_expenses': total_expenses,
                'budget_available': budget_available
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
    amount = ndb.StringProperty()
    date = ndb.DateProperty()
    time = ndb.TimeProperty(auto_now_add=True)
    
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
            transaction.amount = amount
            transaction.date = date
            transaction.put()

            # construct or update UserSummary object and store into database
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.year == datetime.datetime.now().year, UserSummary.month == datetime.datetime.now().month).fetch()
            if len(user_summary) == 1:
                summary = user_summary[0]
            else:
                summary = UserSummary()
                summary.initialization()

            # update total tag amount
            if tag == 'food':
                summary.total_food_expenses = two_digits(str(float(summary.total_food_expenses) + float(amount)))
            elif tag == 'entertainment':
                summary.total_entertainment_expenses = two_digits(str(float(summary.total_entertainment_expenses) + float(amount)))
            elif tag == 'accommodation':
                summary.total_accommodation_expenses = two_digits(str(float(summary.total_accommodation_expenses) + float(amount)))
            elif tag == 'transport':
                summary.total_transport_expenses = two_digits(str(float(summary.total_transport_expenses) + float(amount)))
            elif tag == 'savings':
                summary.total_savings = two_digits(str(float(summary.total_savings) + float(amount)))
            elif tag == 'others':
                summary.total_others_expenses = two_digits(str(float(summary.total_others_expenses) + float(amount)))
            elif tag == 'income':
                summary.total_income = two_digits(str(float(summary.total_income) + float(amount)))

            # update total_expenses
            if tag != 'income' and tag != 'savings':
                summary.total_expenses = two_digits(str(float(summary.total_expenses) + float(amount)))

            # update available budget_available
            if tag != 'income':
                summary.budget_available = two_digits(str(float(summary.budget_available) - float(amount)))

            summary.put()

            # render webpage
            template = jinja_environment.get_template('transactionsuccessful.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)
                
class MonthlyBudgetPage(webapp2.RequestHandler):
    """ Handler for monthly budget page"""

    def get(self):
        user = users.get_current_user()
                        
        if user: #signed in already
            
            info = Budgets.query(Budgets.user == user, Budgets.period == 'Monthly').fetch()
            #initialize value to empty string
            food = ''
            entertainment = ''
            accommodation = ''
            transport = ''
            others = ''

            if len(info) == 1: #monthly budget was set before
                #convert float into two digits string
                food = two_digits(info[0].food)
                entertainment = two_digits(info[0].entertainment)
                accommodation = two_digits(info[0].accommodation)
                transport = two_digits(info[0].transport)
                others = two_digits(info[0].others)
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'food': food,
                'entertainment': entertainment,
                'accommodation': accommodation,
                'transport': transport,
                'others': others
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
            info = Budgets.query(Budgets.user == user, Budgets.period == 'Yearly').fetch()
            #initialize value to empty string
            food = ''
            entertainment = ''
            accommodation = ''
            transport = ''
            others = ''

            if len(info) == 1: #yearly budget was set before
                #convert float into two digits string
                food = two_digits(info[0].food)
                entertainment = two_digits(info[0].entertainment)
                accommodation = two_digits(info[0].accommodation)
                transport = two_digits(info[0].transport)
                others = two_digits(info[0].others)
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'food': food,
                'entertainment': entertainment,
                'accommodation': accommodation,
                'transport': transport,
                'others': others
            }
            template = jinja_environment.get_template('yearlybudget.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class Budgets(ndb.Model):
    # Models a budget which contain every tags' amount and period(monthly or yearly)
    user = ndb.UserProperty(auto_current_user_add=True)
    month = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    period = ndb.StringProperty()
    food = ndb.StringProperty()
    entertainment = ndb.StringProperty()
    accommodation = ndb.StringProperty()
    transport = ndb.StringProperty()
    others = ndb.StringProperty()

class BudgetSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the budget set successful page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            #get the value from transaction form
            period = self.request.get('setbudget').split(' ')[1]
            food = two_digits(self.request.get('food'))
            entertainment = two_digits(self.request.get('entertainment'))
            accommodation = two_digits(self.request.get('accommodation'))
            transport = two_digits(self.request.get('transport'))
            others = two_digits(self.request.get('others'))
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'period': period,
                'food': food,
                'entertainment': entertainment,
                'accommodation': accommodation,
                'transport': transport,
                'others': others
            }

            # construct or update Budgets object and store into database
            if period == 'Monthly': #check if budget of current year and month exists
                old_budgets = Budgets.query(Budgets.user == user, Budgets.period == period, Budgets.month == datetime.datetime.now().month, Budgets.year == datetime.datetime.now().year).fetch()    
            elif period == 'Yearly': #check if budget of current year exists
                old_budgets = Budgets.query(Budgets.user == user, Budgets.period == period, Budgets.year == datetime.datetime.now().year).fetch()
                
            if len(old_budgets) == 1:
                budgets = old_budgets[0]
            else:
                budgets = Budgets()

            budgets.month = datetime.datetime.now().month
            budgets.year = datetime.datetime.now().year
            budgets.period = period
            budgets.food = food
            budgets.entertainment = entertainment
            budgets.accommodation = accommodation
            budgets.transport = transport
            budgets.others = others
            budgets.put()

            # construct or update UserSummary object
            user_summary = UserSummary.query(UserSummary.user == user).fetch()
            if len(user_summary) == 1:
                summary = user_summary[0]
            else:
                summary = UserSummary()
                summary.initialization()
                
            summary.total_budget = two_digits(str(float(food) + float(entertainment) + float(accommodation) + float(transport) + float(others)))
            summary.budget_available = two_digits(str(float(summary.total_budget) - float(summary.total_expenses)))
            summary.put()
            
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
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month, UserSummary.year == datetime.datetime.now().year).fetch()
            budgets = Budgets.query(Budgets.user == user, Budgets.period == "Monthly", Budgets.month == datetime.datetime.now().month).fetch()

            # initialize the variable in summary and retrieve if exists
            total_income = "0.00"
            total_savings = "0.00"
            total_budget = "0.00"
            total_expenses = "0.00"
            total_food_expenses = "0.00"
            total_entertainment_expenses = "0.00"
            total_accommodation_expenses = "0.00"
            total_transport_expenses = "0.00"
            total_others_expenses = "0.00"
            total_food_budget = "0.00"
            total_entertainment_budget = "0.00"
            total_accommodation_budget = "0.00"
            total_transport_budget = "0.00"
            total_others_budget = "0.00"

            if len(user_summary) == 1: # user summary exists
                total_income = user_summary[0].total_income
                total_savings = user_summary[0].total_savings
                total_budget = user_summary[0].total_budget
                total_expenses = user_summary[0].total_expenses
                total_food_expenses = user_summary[0].total_food_expenses
                total_entertainment_expenses = user_summary[0].total_entertainment_expenses
                total_accommodation_expenses = user_summary[0].total_accommodation_expenses
                total_transport_expenses = user_summary[0].total_transport_expenses
                total_others_expenses = user_summary[0].total_others_expenses
            if len(budgets) == 1: # budget exists
                total_food_budget = budgets[0].food
                total_entertainment_budget = budgets[0].entertainment
                total_accommodation_budget = budgets[0].accommodation
                total_transport_budget = budgets[0].transport
                total_others_budget = budgets[0].others
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'total_income': total_income,
                'total_savings': total_savings,
                'total_budget': total_budget,
                'total_expenses': total_expenses,
                'total_food_expenses': total_food_expenses,
                'total_entertainment_expenses': total_entertainment_expenses,
                'total_accommodation_expenses': total_accommodation_expenses,
                'total_transport_expenses': total_transport_expenses,
                'total_others_expenses': total_others_expenses,
                'total_food_budget': total_food_budget,
                'total_entertainment_budget': total_entertainment_budget,
                'total_accommodation_budget': total_accommodation_budget,
                'total_transport_budget': total_transport_budget,
                'total_others_budget': total_others_budget
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
            history = Transaction.query(Transaction.user == user).order(-Transaction.time).fetch()

            # initialize the variable in transaction history and retrieve if exists
            date = 'none'
            tag = 'none'
            description = 'none'
            amount = 'none'
            if len(history) > 0: # transaction record exists
                date = history[0].date
                tag = history[0].tag
                description = history[0].description
                amount = history[0].amount
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'date': date,
                'tag': tag,
                'desc': description,
                'amount': amount,
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
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month, UserSummary.year == datetime.datetime.now().year).fetch()

            # initialize the variable in summary and retrieve if exists
            total_savings = "0.00"
            total_food_expenses = "0.00"
            total_entertainment_expenses = "0.00"
            total_accommodation_expenses = "0.00"
            total_transport_expenses = "0.00"
            total_others_expenses = "0.00"

            if len(user_summary) == 1: # user summary exists
                total_savings = user_summary[0].total_savings
                total_food_expenses = user_summary[0].total_food_expenses
                total_entertainment_expenses = user_summary[0].total_entertainment_expenses
                total_accommodation_expenses = user_summary[0].total_accommodation_expenses
                total_transport_expenses = user_summary[0].total_transport_expenses
                total_others_expenses = user_summary[0].total_others_expenses
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'total_savings': total_savings,
                'total_food_expenses': total_food_expenses,
                'total_entertainment_expenses': total_entertainment_expenses,
                'total_accommodation_expenses': total_accommodation_expenses,
                'total_transport_expenses': total_transport_expenses,
                'total_others_expenses': total_others_expenses,
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
