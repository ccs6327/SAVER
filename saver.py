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

app = webapp2.WSGIApplication([('/user', UserPage)],
                              debug=True)
