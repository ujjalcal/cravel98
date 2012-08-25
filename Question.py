from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
from Answer import *
from Base import *

class Question(ndb.Model):
	question = ndb.StringProperty()
	qurl = ndb.StringProperty()
	answers = ndb.StructuredProperty(Answer)

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
		
	def render(self, view=False):
	    logging.error('in Question render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-question.html", q = self, view=view)

	
	@classmethod
	def getQuestionByName(self, question):
		questions = Question.query().filter(Question.question == question)
		return questions

	@classmethod
	def getQuestionByPath(self, path):
		questions = Question.query().filter(Question.qurl == path)
		return questions
		
	@classmethod
	def getAllQuestions(update=True):
	    	#key = 'top'
	    	#dests = memcache.get(key)
		    	
	    	#if dests is None or update:
	    	logging.error('DB Query')
	    	questions = Question.query()
	    	#	memcache.set(key, dests)
		#else:
		#	logging.error('No DB Query')
		    
    		return questions
