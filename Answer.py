from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

from Destination1 import *
from Trip  import *
from Base import *


class Answer(ndb.Model):
	ansText = ndb.TextProperty()
	destinations = ndb.KeyProperty(Destination1, repeated = True)
	trips = ndb.KeyProperty(Trip, repeated = True)
	

	added_by = ndb.KeyProperty(User)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_updated_by = ndb.KeyProperty(User)
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
