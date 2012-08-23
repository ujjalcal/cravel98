import os
import re
import random
import hashlib
import hmac
from string import letters
import json
import logging
import time

import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import memcache


class Destination(db.Model):
	name = db.StringProperty()
	location = db.StringProperty()
	type = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	lastModified = db.DateTimeProperty(auto_now = True)
	picture = db.Blob()
	video = db.Blob()
	links = db.StringProperty()
	
	def render(self):
	    logging.error('in Destination render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_str("cravel-content.html", d = self)

	
	@classmethod
	def getDestinationByName(self, name):
		dest = db.GqlQuery("select * from Destination where name = '%s'" % name);
		return dest
		
	@classmethod
	def getDestinationByLocation():
		dest = db.GqlQuery("");
		return dest
		
	@classmethod
	def getDestinationByTypeNearLocation():
		dest = db.GqlQuery("");
		return dest
		
	@classmethod
	def getAllDestinations(update=True):
	    	#key = 'top'
	    	#dests = memcache.get(key)
		    	
	    	#if dests is None or update:
	    	logging.error('DB Query')
	    	dests = Destination.all().order('-created')
	    	#	memcache.set(key, dests)
		#else:
		#	logging.error('No DB Query')
		    
    		return dests



class Trips(db.Model):
	name = db.StringProperty()
	created = db.DateTimeProperty()
	createdBy = db.StringProperty()
	
class TripDestination(db.Model):
	trip_id = db.StringProperty()
	dest_id = db.StringProperty()
	

class UserTrips(db.Model):
	user_id = db.StringProperty()
	trip_id = db.StringProperty()
	
class VoteOnTrips(db.Model):
	trip_id = db.StringProperty()
	votes = db.StringProperty()
	
class Question(db.Model):
	question = db.StringProperty()
	asked_by = db.StringProperty()
	
class Answer_Trip(db.Model):
	trip_dest_id = db.StringProperty()
	question_id = db.StringProperty()
	
class Answer_Destination(db.Model):
	dest_id = db.StringProperty()
	question_id = db.StringProperty()
	
class Answer_Comment(db.Model):
	comment = db.StringProperty()
	question_id = db.StringProperty()
	
class Answer_Link(db.Model):
	link = db.StringProperty()
	question_id = db.StringProperty()
	
	
class Interest(db.Model):
	interest = db.StringProperty()
	
	
	