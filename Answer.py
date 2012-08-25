from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

from Destination1 import *
from Trip  import *
from Base import *


class Answer(ndb.Model):
	destinations = ndb.StructuredProperty(Destination1, repeated = True)
	trips = ndb.StructuredProperty(Trip)
	ansText = ndb.TextProperty()

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
	
	
	def render(ans, view=False):
	    logging.error('in Answer render:')
	    logging.error(ans)	
	   #self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-answer.html", a = ans)

	@classmethod
	def renderAnsForm(view=False):
	    logging.error('in render Answer form:')
	    return render_jinja_str("answerForm.html")
