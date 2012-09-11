from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

from Base import *
from Users import *


class Tag(ndb.Model):
	name = ndb.StringProperty()
	search_name = ndb.StringProperty()
	destinations = ndb.KeyProperty(repeated = True)
	trips = ndb.KeyProperty(repeated = True)
	questions = ndb.KeyProperty(repeated = True)
	
	added_by = ndb.KeyProperty(User)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_updated_by = ndb.KeyProperty(User)
	lastModified = ndb.DateTimeProperty(auto_now = True)
	
  	def _pre_put_hook(self):
		self.search_name = self.name.upper()
	
	
	def render(self, view=False):
	    logging.error('in Trip render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-trip.html", t = self, view=view)

	
	@classmethod
	def getTagByName(self, name):
		name = name.upper()
		tags = Tag.query().filter(Tag.search_name == name)
		return tags

	@classmethod
	def getAllTags(update=True):
	    	tags = Tag.query().order(-Tag.created)
		    
    		return tags
    		
'''	@classmethod
	def getAllDestinationsByTagNames(self, *names):
		Tag.query().filter(
'''		