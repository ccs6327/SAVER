import webapp2
import jinja2
import os
import datetime
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

#global function
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

def del_datastore_if_outdated():
    # calculate the latest date to be kept
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    date_to_be_kept = datetime.date(day = 1, month = current_month, year = current_year - 1)
    
    # clear outdated summary data
    summaries = UserSummary.query().fetch()                                        
    for summary in summaries:
        summary_date = datetime.date(day = 1, month = summary.month, year = summary.year)
        if summary_date < date_to_be_kept:
            summary.key.delete()

    # clear outdated transaction data
    transactions = Transaction.query().fetch()
    for transaction in transactions:
        if transaction.date < date_to_be_kept:
            transaction.key.delete()
    
#Datastore Definition
class UserSummary(ndb.Model):
    # Models a summary of user's total expenses, budgets, incomes, savings etc
    user = ndb.UserProperty(auto_current_user_add=True)
    month = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    total_income = ndb.StringProperty()
    total_savings = ndb.StringProperty()
    total_monthly_budget = ndb.StringProperty()
    total_yearly_budget = ndb.StringProperty()
    total_expenses = ndb.StringProperty()
    total_food_expenses = ndb.StringProperty()
    total_entertainment_expenses = ndb.StringProperty()
    total_accommodation_expenses = ndb.StringProperty()
    total_transport_expenses = ndb.StringProperty()
    total_savings_expenses = ndb.StringProperty()
    total_others_expenses = ndb.StringProperty()
    monthly_budget_available = ndb.StringProperty()
    yearly_budget_available = ndb.StringProperty()

    def initialization(self): # initialize all variable to "0.00"
        self.month = datetime.datetime.now().month
        self.year = datetime.datetime.now().year
        self.total_income = "0.00"
        self.total_savings = "0.00"
        self.total_monthly_budget = "0.00"
        self.total_yearly_budget = "0.00"
        self.total_expenses = "0.00"
        self.total_food_expenses = "0.00"
        self.total_entertainment_expenses = "0.00"
        self.total_accommodation_expenses = "0.00"
        self.total_transport_expenses = "0.00"
        self.total_savings_expenses = "0.00"
        self.total_others_expenses = "0.00"
        self.monthly_budget_available = "0.00"
        self.yearly_budget_available = "0.00"

    def del_if_empty(self): # delete self if contain no info
        if self.total_income == '0.00' and self.total_savings == '0.00' and self.total_monthly_budget == '0.00' and self.total_yearly_budget == '0.00' and self.total_expenses == '0.00':
            self.key.delete()

class Transaction(ndb.Model):
    # Models a transaction with description, tag, amount, date.
    user = ndb.UserProperty(auto_current_user_add = True)
    ID = ndb.IntegerProperty()
    description = ndb.StringProperty()
    tag = ndb.StringProperty()
    amount = ndb.StringProperty()
    date = ndb.DateProperty()
    added_time = ndb.DateTimeProperty(auto_now_add = True)
    
class Budgets(ndb.Model):
    # Models a budget which contain every tags' amount and period(monthly or yearly)
    user = ndb.UserProperty(auto_current_user_add = True)
    period = ndb.StringProperty()
    food = ndb.StringProperty()
    entertainment = ndb.StringProperty()
    accommodation = ndb.StringProperty()
    transport = ndb.StringProperty()
    others = ndb.StringProperty()
    
class Tips(ndb.Expando):
    # Models a tips with title, content and date.
    user = ndb.UserProperty(auto_current_user_add = True)
    ID = ndb.IntegerProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)
    score = ndb.IntegerProperty()
    email_list = ndb.StringProperty(repeated=True)

class Leaderboard(ndb.Model):
    # Models a leaderboard with score.
    user = ndb.UserProperty(auto_current_user_add = True)
    score = ndb.IntegerProperty()
    
#Handler
class UserPage(webapp2.RequestHandler):
    """ Handler for the front page after user login."""

    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            del_datastore_if_outdated()
            
            summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month, UserSummary.year == datetime.datetime.now().year).fetch()
            history = Transaction.query(Transaction.user == user).order(-Transaction.added_time).fetch()
            leaderboard = Leaderboard.query().order(-Leaderboard.score).fetch()

            top_users = []
            
            for user_leaderboard in leaderboard:
                top_users.append(user_leaderboard.user.nickname())

            transaction = ""
            # initialize the variable in transaction history and retrieve if exists
            if len(history) > 0: # transaction record exists
                transaction = history[0]

            # initialize value of total_expenses and budget_available and retrieve if exists
            total_expenses = '0.00'
            monthly_budget_available = '0.00'
            yearly_budget_available = '0.00'
            if len(summary) == 1: #does contain user summary
                total_expenses = summary[0].total_expenses
                monthly_budget_available = summary[0].monthly_budget_available
                yearly_budget_available = summary[0].yearly_budget_available
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'total_expenses': total_expenses,
                'monthly_budget_available': monthly_budget_available,
                'yearly_budget_available': yearly_budget_available,
                'transaction': transaction,
                'top_users': top_users
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
            del_datastore_if_outdated()
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('manage.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class DeleteTransaction(webapp2.RequestHandler):
    """ Handler to delete transaction history"""

    def post(self):
        user = users.get_current_user()
        transaction_to_be_deleted = Transaction.get_by_id(int(self.request.get('entity_id')))
        address = self.request.get('address')

        transaction_date = transaction_to_be_deleted.date
    
        template_values = {
            'user_mail': users.get_current_user().email(),
            'logout': users.create_logout_url(self.request.host_url),
            'transaction': transaction_to_be_deleted,
            'address': address,
        }
        transaction_to_be_deleted.key.delete()

        #retrieve UserSummary object and update it after deletion
        summary = UserSummary.query(UserSummary.user == user, UserSummary.year == transaction_date.year, UserSummary.month == transaction_date.month).fetch()[0]

        # set the variable tag and amount
        tag = transaction_to_be_deleted.tag
        amount = transaction_to_be_deleted.amount

        # update total tag amount
        if tag == 'food':
            summary.total_food_expenses = two_digits(str(float(summary.total_food_expenses) - float(amount)))
        elif tag == 'entertainment':
            summary.total_entertainment_expenses = two_digits(str(float(summary.total_entertainment_expenses) - float(amount)))
        elif tag == 'accommodation':
            summary.total_accommodation_expenses = two_digits(str(float(summary.total_accommodation_expenses) - float(amount)))
        elif tag == 'transport':
            summary.total_transport_expenses = two_digits(str(float(summary.total_transport_expenses) - float(amount)))
        elif tag == 'savings':
            summary.total_savings = two_digits(str(float(summary.total_savings) - float(amount)))
        elif tag == 'others':
            summary.total_others_expenses = two_digits(str(float(summary.total_others_expenses) - float(amount)))
        elif tag == 'income':
            summary.total_income = two_digits(str(float(summary.total_income) - float(amount)))

        # update total_expenses
        if tag != 'income' and tag != 'savings':
            summary.total_expenses = two_digits(str(float(summary.total_expenses) - float(amount)))

        # update available budget_available
        if tag != 'income':
            summary.monthly_budget_available = two_digits(str(float(summary.monthly_budget_available) + float(amount)))
        summary.put()

        summary.del_if_empty()
        
        if transaction_to_be_deleted.date.year == datetime.datetime.now().year:
            summaries = UserSummary.query(UserSummary.user == user).fetch()
            for summary in summaries:
                if summary.year == datetime.datetime.now().year and summary.month >= transaction_to_be_deleted.date.month:
                    summary.yearly_budget_available = two_digits(str(float(summary.yearly_budget_available) + float(amount)))
                    summary.put()
        
        template = jinja_environment.get_template('transactiondeletedsuccessful.html')
        self.response.out.write(template.render(template_values))

class TransactionPage(webapp2.RequestHandler):
    """ Handler for the add new transaction page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            del_datastore_if_outdated()
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('transaction.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)
    
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
                'date': date,
            }

            # construct Transaction object and store into database
            transaction = Transaction()
            transaction.description = description
            transaction.tag = tag
            transaction.amount = amount
            transaction.date = date
            transaction.put()
            transaction.ID = int(transaction.key.id())
            transaction.put()

            # construct or update UserSummary object and store into database
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.year == year, UserSummary.month == month).fetch()
            if len(user_summary) == 1:
                summary = user_summary[0]
            else:
                summary = UserSummary()
                summary.initialization()
                # prevents user first add previous month transactions in current month
                if summary.month != month:
                    summary.month = month
                if summary.year != year:
                    summary.year = year

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
                summary.monthly_budget_available = two_digits(str(float(summary.monthly_budget_available) - float(amount)))

            summary.put()
        
            if transaction.date.year == datetime.datetime.now().year:
                summaries = UserSummary.query(UserSummary.user == user).fetch()
                for summary in summaries:
                    if summary.year == datetime.datetime.now().year and summary.month >= transaction.date.month:
                        summary.yearly_budget_available = two_digits(str(float(summary.yearly_budget_available) - float(amount)))
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
            del_datastore_if_outdated()
            
            budgets = Budgets.query(Budgets.user == user, Budgets.period == 'Monthly').fetch()
            summary = UserSummary.query(UserSummary.user == user).fetch()
            #initialize value to empty string
            monthly_budget = {'food' : '0.00', 'entertainment' : '0.00', 'accommodation' : '0.00', 'transport' : '0.00', 'others' : '0.00'}
            
            if len(budgets) == 1: #monthly budget was set before
                monthly_budget['food'] = budgets[0].food
                monthly_budget['entertainment'] = budgets[0].entertainment
                monthly_budget['accommodation'] = budgets[0].accommodation
                monthly_budget['transport'] = budgets[0].transport
                monthly_budget['others'] = budgets[0].others
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'monthly_budget': monthly_budget
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
            del_datastore_if_outdated()
            
            budgets = Budgets.query(Budgets.user == user, Budgets.period == 'Yearly').fetch()
            summary = UserSummary.query(UserSummary.user == user).fetch()
            #initialize value to empty string
            yearly_budget = {'food' : '0.00', 'entertainment' : '0.00', 'accommodation' : '0.00', 'transport' : '0.00', 'others' : '0.00'}

            if len(budgets) == 1: #yearly budget was set before
                yearly_budget['food'] = budgets[0].food
                yearly_budget['entertainment'] = budgets[0].entertainment
                yearly_budget['accommodation'] = budgets[0].accommodation
                yearly_budget['transport'] = budgets[0].transport
                yearly_budget['others'] = budgets[0].others
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'yearly_budget': yearly_budget
            }
            template = jinja_environment.get_template('yearlybudget.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class BudgetSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the budget set successful page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            #get the value from transaction form
            period = self.request.get('setbudget').split(' ')[1]

            # construct or update Budgets object and store into database
            if period == 'Monthly': #check if budget of current year and month exists
                old_budgets = Budgets.query(Budgets.user == user, Budgets.period == period).fetch()    
            elif period == 'Yearly': #check if budget of current year exists
                old_budgets = Budgets.query(Budgets.user == user, Budgets.period == period).fetch()
                
            if len(old_budgets) == 1:
                budgets = old_budgets[0]
            else:
                budgets = Budgets()

            budgets.period = period
            budgets.food = two_digits(self.request.get('food'))
            budgets.entertainment = two_digits(self.request.get('entertainment'))
            budgets.accommodation = two_digits(self.request.get('accommodation'))
            budgets.transport = two_digits(self.request.get('transport'))
            budgets.others = two_digits(self.request.get('others'))
            budgets.put()

            # construct or update UserSummary object  
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month).fetch()
            # construct if not exist
            if len(user_summary) == 1:
                summary = user_summary[0]
            else:
                summary = UserSummary()
                summary.initialization()
            # update accordingly to the period
            budget_sum = float(budgets.food) + float(budgets.entertainment) + float(budgets.accommodation) + float(budgets.transport) + float(budgets.others)
            if period == 'Monthly':
                summary.total_monthly_budget = two_digits(budget_sum)
                summary.monthly_budget_available = two_digits(float(summary.total_monthly_budget) - float(summary.total_expenses))
            elif period == 'Yearly':
                summary.total_yearly_budget = two_digits(budget_sum)
                # count total year expenses
                total_yearly_expenses = 0
                for monthly_summary in user_summary:
                    if monthly_summary.year == datetime.datetime.now().year: # current year month summary
                        total_yearly_expenses += float(monthly_summary.total_expenses)
                summary.yearly_budget_available = two_digits(float(summary.total_yearly_budget) - total_yearly_expenses) 
            summary.put()

            summary.del_if_empty()
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'budgets': budgets
            }
            
            template = jinja_environment.get_template('budgetsuccessful.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class OverviewPage(webapp2.RequestHandler):
    """ Handler for the transaction successful page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            del_datastore_if_outdated()

            # construct info for current date
            today = datetime.datetime.now()
            last_month = datetime.date(day = 1, month = today.month - 1, year = today.year)
            two_month_before = datetime.date(day = 1, month = today.month - 2, year = today.year)
            three_month_before = datetime.date(day = 1, month = today.month - 3, year = today.year)

            # check if past summary info exists
            exist = {'last_month': False, 'two_month_before': False, 'three_month_before': False}
            summary = UserSummary.query(UserSummary.user == user, UserSummary.year == last_month.year, UserSummary.month == last_month.month).fetch()
            if len(summary) == 1:
                exist['last_month'] = True
            summary = UserSummary.query(UserSummary.user == user, UserSummary.year == two_month_before.year, UserSummary.month == two_month_before.month).fetch()
            if len(summary) == 1:
                exist['two_month_before'] = True
            summary = UserSummary.query(UserSummary.user == user, UserSummary.year == three_month_before.year, UserSummary.month == three_month_before.month).fetch()
            if len(summary) == 1:
                exist['three_month_before'] = True
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'current_month': today.strftime('%B %Y'),
                'exist': exist,
                'last_month': last_month.strftime('%B %Y'),
                'two_month_before': two_month_before.strftime('%B %Y'),
                'three_month_before': three_month_before.strftime('%B %Y'),
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
            del_datastore_if_outdated()
            
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month, UserSummary.year == datetime.datetime.now().year).fetch()
            budgets = Budgets.query(Budgets.user == user, Budgets.period == "Monthly").fetch()

            # initialize the variable in summary and retrieve if exists
            summary = {'total_income': '0.00',
                       'total_savings': '0.00',
                       'total_monthly_budget': '0.00',
                       'total_expenses': '0.00',
                       'total_food_expenses' : '0.00',
                       'total_entertainment_expenses' : '0.00',
                       'total_accommodation_expenses' : '0.00',
                       'total_transport_expenses' : '0.00',
                       'total_others_expenses' : '0.00',
                       'total_food_budget' : '0.00',
                       'total_entertainment_budget' : '0.00',
                       'total_accommodation_budget' : '0.00',
                       'total_transport_budget' : '0.00',
                       'total_others_budget' : '0.00'}

            if len(user_summary) == 1: # user summary exists
                summary['total_income'] = user_summary[0].total_income
                summary['total_savings'] = user_summary[0].total_savings
                summary['total_monthly_budget'] = user_summary[0].total_monthly_budget
                summary['total_expenses'] = user_summary[0].total_expenses
                summary['total_food_expenses'] = user_summary[0].total_food_expenses
                summary['total_entertainment_expenses'] = user_summary[0].total_entertainment_expenses
                summary['total_accommodation_expenses'] = user_summary[0].total_accommodation_expenses
                summary['total_transport_expenses'] = user_summary[0].total_transport_expenses
                summary['total_others_expenses'] = user_summary[0].total_others_expenses
            if len(budgets) == 1: # budget exists
                summary['total_food_budget'] = budgets[0].food
                summary['total_entertainment_budget'] = budgets[0].entertainment
                summary['total_accommodation_budget'] = budgets[0].accommodation
                summary['total_transport_budget'] = budgets[0].transport
                summary['total_others_budget'] = budgets[0].others
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'summary': summary
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
            del_datastore_if_outdated()
            
            transactions = Transaction.query().order(Transaction.added_time).fetch()

            if self.request.get('current_index'):
                current_index = int(self.request.get('current_index'))
            else:
                current_index = 0

            if self.request.get('navigation') == 'left' and current_index - 5 >= 0:
                current_index = current_index - 5
            elif self.request.get('navigation') == 'right' and current_index + 5 < len(transactions):
                current_index = current_index + 5
    
            transactions_size = len(transactions)

            if len(transactions) > current_index + 5:
                transactions = transactions[current_index:current_index + 5]
            else:
                transactions = transactions[current_index:len(transactions)]
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'transactions': transactions,
                'current_index': current_index,
                'transactions_size': transactions_size,
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
            del_datastore_if_outdated()
            
            user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == datetime.datetime.now().month, UserSummary.year == datetime.datetime.now().year).fetch()

            # initialize the variable in summary and retrieve if exists
            summary = {'total_savings': '0.00',
                       'total_food_expenses': '0.00',
                       'total_entertainment_expenses': '0.00',
                       'total_accommodation_expenses': '0.00',
                       'total_transport_expenses': '0.00',
                       'total_others_expenses': '0.00'}

            if len(user_summary) == 1: # user summary exists
                summary['total_savings'] = user_summary[0].total_savings
                summary['total_food_expenses'] = user_summary[0].total_food_expenses
                summary['total_entertainment_expenses'] = user_summary[0].total_entertainment_expenses
                summary['total_accommodation_expenses'] = user_summary[0].total_accommodation_expenses
                summary['total_transport_expenses'] = user_summary[0].total_transport_expenses
                summary['total_others_expenses'] = user_summary[0].total_others_expenses
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.datetime.now().strftime('%B'),
                'summary': summary
            }
            template = jinja_environment.get_template('chartview.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class PastSummaryPage(webapp2.RequestHandler):
    """ Handler for the past summary page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already

            # get user summary and budgets of the month requested
            if self.request.get('month'):
                requested_month = datetime.datetime.now().month - int(self.request.get('month'))
                requested_year = datetime.datetime.now().year
                if requested_month < 0: # last year
                    requested_month = requested_month + 12
                    requested_year = requested_year - 1
                user_summary = UserSummary.query(UserSummary.user == user, UserSummary.month == requested_month, UserSummary.year == requested_year).fetch()
                budgets = Budgets.query(Budgets.user == user).fetch()
            else:
                self.redirect(self.request.host_url)

            # initialize the variable in summary and retrieve if exists
            summary = {'total_income': '0.00',
                       'total_savings': '0.00',
                       'total_monthly_budget': '0.00',
                       'total_expenses': '0.00',
                       'total_food_expenses' : '0.00',
                       'total_entertainment_expenses' : '0.00',
                       'total_accommodation_expenses' : '0.00',
                       'total_transport_expenses' : '0.00',
                       'total_others_expenses' : '0.00',
                       'total_food_budget' : '0.00',
                       'total_entertainment_budget' : '0.00',
                       'total_accommodation_budget' : '0.00',
                       'total_transport_budget' : '0.00',
                       'total_others_budget' : '0.00'}

            if len(user_summary) == 1: # user summary exists
                summary['total_income'] = user_summary[0].total_income
                summary['total_savings'] = user_summary[0].total_savings
                summary['total_monthly_budget'] = user_summary[0].total_monthly_budget
                summary['total_expenses'] = user_summary[0].total_expenses
                summary['total_food_expenses'] = user_summary[0].total_food_expenses
                summary['total_entertainment_expenses'] = user_summary[0].total_entertainment_expenses
                summary['total_accommodation_expenses'] = user_summary[0].total_accommodation_expenses
                summary['total_transport_expenses'] = user_summary[0].total_transport_expenses
                summary['total_others_expenses'] = user_summary[0].total_others_expenses
            if len(budgets) == 1: # budget exists
                summary['total_food_budget'] = budgets[0].food
                summary['total_entertainment_budget'] = budgets[0].entertainment
                summary['total_accommodation_budget'] = budgets[0].accommodation
                summary['total_transport_budget'] = budgets[0].transport
                summary['total_others_budget'] = budgets[0].others
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'month': datetime.date(day = 1, month = requested_month, year = requested_year).strftime('%B'),
                'summary': summary
            }
            template = jinja_environment.get_template('pastsummary.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class LeaderboardPage(webapp2.RequestHandler):
    """ Handler for the leaderboard page"""

    def get(self):
        user = users.get_current_user()
        if user: #signed in already
            leaderboard = Leaderboard.query().order(-Leaderboard.score).fetch()
            top_users = []

            for user_leaderboard in leaderboard:
                top_users.append(user_leaderboard.user.nickname())
                
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'top_users': top_users
            }
            template = jinja_environment.get_template('leaderboard.html')
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

            tips = Tips.query().order(-Tips.datetime).fetch()

            if self.request.get('current_index'):
                current_index = int(self.request.get('current_index'))
            else:
                current_index = 0

            if self.request.get('navigation') == 'left' and current_index - 5 >= 0:
                current_index = current_index - 5
            elif self.request.get('navigation') == 'right' and current_index + 5 < len(tips):
                current_index = current_index + 5
    
            tips_size = len(tips)

            if len(tips) > current_index + 5:
                tips = tips[current_index:current_index + 5]
            else:
                tips = tips[current_index:len(tips)]

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'tips': tips,
                'current_index': current_index,
                'tips_size': tips_size
            }
            template = jinja_environment.get_template('tipssharing.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class SharingSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the tips sharing page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already
            tips = Tips()
            tips.title = self.request.get('Title')
            tips.content = self.request.get('Content')
            tips.score = 0
            temp_email_list = tips.email_list
            temp_email_list.append(users.get_current_user().email())
            tips.email_list = temp_email_list
            tips.put()
            tips.ID = int(tips.key.id())
            tips.put()
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'tips': tips,
            }
            template = jinja_environment.get_template('tipssharingsuccessful.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class SharingPostPage(webapp2.RequestHandler):
    """ Handler for the tips sharing page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            tips = Tips.get_by_id(int(self.request.get('entity_id')))
            voted = False
            
            for email in tips.email_list:
                if user.email() == email:
                    voted = True
                    break
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'tips': tips,
                'current_index': self.request.get('current_index'),
                'voted': voted,
            }
            
            template = jinja_environment.get_template('tipssharingpost.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class RatingSuccessfulPage(webapp2.RequestHandler):
    """ Handler for the rating successful page"""

    def post(self):
        user = users.get_current_user()
        if user: #signed in already

            tips = Tips.get_by_id(int(self.request.get('entity_id')))
            leaderboard = Leaderboard.query(Leaderboard.user == tips.user).fetch()

            # create or retrieve leaderboard object
            if len(leaderboard) == 1:
                leaderboard = leaderboard[0]
            else:
                leaderboard = Leaderboard()
                leaderboard.user = tips.user
                leaderboard.score = 0
                leaderboard.put()

            # Add score to the leaderboard and add voter's email to the email list
            result = self.request.get('rating')
            if result:
                if result == "Average":
                    tips.score = tips.score + 1
                    leaderboard.score = leaderboard.score + 1
                elif result == "Good":
                    tips.score = tips.score + 2
                    leaderboard.score = leaderboard.score + 2
                elif result == "Excellent":
                    tips.score = tips.score + 3
                    leaderboard.score = leaderboard.score + 3

                temp_email_list = tips.email_list
                temp_email_list.append(users.get_current_user().email())
                tips.email_list = temp_email_list
                tips.put()
                leaderboard.put()
            
            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
                
            template = jinja_environment.get_template('ratingsuccessful.html')
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
                               ('/pastsummary', PastSummaryPage),
                               ('/leaderboard', LeaderboardPage),
                               ('/about', AboutPage),
                               ('/tipssharingform', TipsSharingFormPage),
                               ('/tipssharing', TipsSharingPage),
                               ('/sharingformsuccessful', SharingSuccessfulPage),
                               ('/sharingpost', SharingPostPage),
                               ('/deletetransaction', DeleteTransaction),
                               ('/ratingsuccessful', RatingSuccessfulPage)],
                               debug=True)
