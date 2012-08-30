from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

from Base import *
from Users import *

class Destination1(ndb.Model):
	name = ndb.StringProperty()
	location = ndb.StringProperty()
	description = ndb.StringProperty()
	details = ndb.StringProperty()
	tags = ndb.StringProperty(repeated = True)
	links = ndb.StringProperty(repeated = True)

	durl = ndb.StringProperty()
		
	added_by = ndb.KeyProperty(User)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_updated_by = ndb.KeyProperty(User)
	lastModified = ndb.DateTimeProperty(auto_now = True)
	
	def render(self, view=False):
	    logging.error('in Destination render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content.html", d = self, view = view)

	
	@classmethod
	def getDestinationByName(self, name):
		dest = Destination1.query().filter(Destination1.name == name)
		return dest
		
	@classmethod
	def getDestinationByLocation():
		dest = ndb.GqlQuery("");
		return dest
		
	@classmethod
	def getDestinationByTypeNearLocation():
		dest = ndb.GqlQuery("");
		return dest
		
	@classmethod
	def getDestinationByPath(self, path):
		destinations = Destination1.query().filter(Destination1.durl == path)
		return destinations

	@classmethod
	def getAllDestinations(update=True):
	    	#key = 'top'
	    	#dests = memcache.get(key)
		    	
	    	#if dests is None or update:
	    	logging.error('DB Query')
	    	dests = Destination1.query() #Destination1.all().order('-created')
	    	#	memcache.set(key, dests)
		#else:
		#	logging.error('No DB Query')
		    
    		return dests
