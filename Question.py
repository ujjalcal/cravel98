from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

from Answer import *
from Base import *
from Users import *

class Question(ndb.Model):
	question = ndb.StringProperty()
	tags = ndb.StringProperty(repeated = True)
	answers = ndb.KeyProperty(Answer, repeated = True)

	qurl = ndb.StringProperty()

	added_by = ndb.KeyProperty(User)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_updated_by = ndb.KeyProperty(User)
	lastModified = ndb.DateTimeProperty(auto_now = True)
		
	def render(self, view=False):
	    logging.error('in Question render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-question.html", q = self, view=view)

	def renderAnsForm(view=False):
	    logging.error('in render Answer form:')
	    return render_jinja_str("answerForm.html")
	
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
	    	questions = Question.query().order(-Question.created)
	    	#	memcache.set(key, dests)
		#else:
		#	logging.error('No DB Query')
		    
    		return questions
    		
	def addedByUser(sefl):    		
		user = self.added_by.kind(),int(self.added_by.id()).get().name
