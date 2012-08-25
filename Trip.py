from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
from Destination1 import *
from Base import *


class Trip(ndb.Model):
	name = ndb.StringProperty()
	links = ndb.StringProperty()
	destinations = ndb.StructuredProperty(Destination1, repeated = True)

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
		
	def render(self):
	    logging.error('in Trip render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-trip.html", t = self)

	
	@classmethod
	def getTripByName(self, name):
		trips = Trip.query().filter(Trip.name == name)
		return trips
		
	@classmethod
	def getAllTrips(update=True):
	    	#key = 'top'
	    	#dests = memcache.get(key)
		    	
	    	#if dests is None or update:
	    	logging.error('DB Query')
	    	trips = Trip.query()
	    	#	memcache.set(key, dests)
		#else:
		#	logging.error('No DB Query')
		    
    		return trips
    		
