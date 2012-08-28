from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
from Destination1 import *
from Base import *


class Trip(ndb.Model):
	name = ndb.StringProperty()
	description = ndb.StringProperty()
	details = ndb.TextProperty()
	links = ndb.StringProperty(repeated = True)
	tags = ndb.StringProperty(repeated = True)
	destinations = ndb.KeyProperty(Destination1, repeated = True)

	turl = ndb.StringProperty()

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
		
	def render(self, view=False):
	    logging.error('in Trip render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-trip.html", t = self, view=view)

	
	@classmethod
	def getTripByName(self, name):
		trips = Trip.query().filter(Trip.name == name)
		return trips

	@classmethod
	def getTripByPath(self, path):
		trips = Trip.query().filter(Trip.turl == path)
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
    		
