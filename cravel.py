import os
import re
import random
import hashlib
import hmac
from string import letters
import json
import logging
import time
import urllib2
import urllib

import webapp2
import jinja2

from Post import *
from Users import *
from Question import *
from Answer import *
from Destination1 import *
from Trip import *
from Base import *

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


db_timer = time.time()

def render_str_final(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)



class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    ##injecting params
    def render_str_inject(self, template, **params):
    	global db_timer
        params['user'] = self.user
        params['curr_time'] = round(time.time() - db_timer)
        params['path'] = self.request.path
      
      	logging.error(params)
        return render_str_final(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str_inject(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class MainPage(BlogHandler):
  def get(self):
      self.write('Hi this is the Cravel - the Youtube for Travel. <br><br> Please goto the <a href="/feed">feed</a> url below to see recent postings.')


class BlogFront(BlogHandler):
    def get(self):
    	global db_timer
        #posts = Post.all().order('-created')
        posts = Post.allPosts()
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        #key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        #post = db.get(key)
        post = Post.permalink(post_id)
        logging.info(post.key().id())

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        global db_timer
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            Post.allPosts(True)
            db_timer = time.time()
            self.redirect('/blog/%s' % str(p.key().id()))
            
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


###### Unit 2 HW's
class Rot13(BlogHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text = rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Unit2Signup(Signup):
    def done(self):
        self.redirect('/unit2/welcome?username=' + self.username)

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Login(BlogHandler):
    def get(self):
    	logging.error('tata')
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class Unit3Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')


class Json(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        #self.render('front_json.html', posts = posts)
        return self.render_json([p.as_dict() for p in posts])
    	
class PermJson(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
	
	self.render_json(post.as_dict())
    	
    	    	
class Flush(BlogHandler):
    def get(self):
    	memcache.flush_all()
    	self.redirect('/blog')
    	
    	
class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')
            
class Wiki(db.Model):
	path = db.StringProperty(required = True)
	subject = db.StringProperty()
	content = db.TextProperty()
	version = db.IntegerProperty(default=0)
        created = db.DateTimeProperty(auto_now_add = True)
    	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
	        self._render_text = self.content.replace('\n', '<br>')
        	return render_str("wiki-content.html", p = self)
	
	@classmethod
	def getWikiBypath(self, path):
		if path:
			wikiObj = db.GqlQuery('Select * from Wiki where path = \'' + path + '\' order by version desc')
			return wikiObj
	@classmethod
	def getWikiByVersion(self, path, version):
		if path:
			wikiObj = db.GqlQuery('Select * from Wiki where path = \'%s\' and version = %s' % (path, str(version)))
			return wikiObj

	def render_hist(self):
	        self._render_text = self.content.replace('\n', '<br>')
	        return render_str("wiki-history.html", q = self)
			

	
class WikiPage(BlogHandler):
   
   def get(self, npath=''):
        user_id = self.read_secure_cookie('user_id')
        
        version = self.request.get('v')
        
        path = self.request.path

        if version:
        	wikiObj = Wiki.getWikiByVersion(path, version)
        else:
	        wikiObj = Wiki.getWikiBypath(path)
        
        if wikiObj and wikiObj.count() > 0:
        	self.render('wiki.html', wiki = wikiObj[0])
    	else:
	    	self.redirect('/question'+path)
    	
   	

class EditWiki(BlogHandler):

   def get(self, path):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
        path = path
        
        #if version:
        #	questionObj = Question.getQuestionByName(path)
        #else:
        questionObj = Question.getQuestionByName(path)
        
        if questionObj and questionObj.count() > 0:
		self.render('wiki-edit.html', q = questionObj[0])
	else:
   		self.render('wiki-edit.html', q = None)
		

      
   def post(self, path):
   	npath = path
   	question = self.request.get('content')
   	
   	
   	if question:
   		wikiObj = Wiki.getWikiBypath(npath)
   		if wikiObj and wikiObj.count() >= 1:
   			wiki = wikiObj[0]
   			#wiki.subject = subject
   			#wiki.content = content
   			version = wiki.version
   			version = version + 1
   			wiki = Wiki(subject = subject, content = content, path = npath, version = version)
   		        wiki.put()
   		else:
   			wiki = Wiki(subject = subject, content = content, path = npath)
   			wiki.put()

	
	self.redirect(npath)
	
class HistoryWiki(BlogHandler):

   def get(self, path):
        user_id = self.read_secure_cookie('user_id')
        
        if not user_id:
        	self.redirect('/login')
        	
        wiki = Wiki.getWikiBypath(path)
        
        if wiki and wiki.count() > 0:
	    #self.render('wiki-history.html', wikis = wiki)
	    self.render('wiki-history_front.html', wikis = wiki)
	else:
   	    #self.render('wiki-history.html', wikis = None)
   	    self.render('wiki-history_front.html', wikis = None)
		

      
   def post(self, path):
   	npath = path
   	content = self.request.get('content')
   	subject = self.request.get('subject')
   	
   	if subject or content:
   		wikiObj = Wiki.getWikiBypath(npath)
   		if wikiObj and wikiObj.count() >= 1:
   			wiki = wikiObj[0]
   			wiki.subject = subject
   			wiki.content = content
   		        wiki.put()
   		else:
   			wiki = Wiki(subject = subject, content = content, path = npath)
   			wiki.put()
	self.redirect(npath)
	
        
        
	
class ErrorWiki(BlogHandler):
	def get(self):
		self.response.out.write("invalid url, it should be /_edit/some path")





	

class Cravel(BlogHandler):
	def get(self):
	
		logging.error('Cravel.get')
		#self.loadData()

	        user_id = self.read_secure_cookie('user_id')
        	
	        search = self.request.get('search')
	        logging.error('search:'+search)
	        
	        if search:
	        	destinations = Destination1.getDestinationByName(search)
		else:	
			destinations = Destination1.getAllDestinations()
			
		if search:
			trips = Trip.getTripByName(search)
		else:	
			trips = Trip.getAllTrips()
		
		if search:
			questions = Question.getQuestionByName(search)
		else:	
			questions = Question.getAllQuestions()


		#logging.error(dest)
        
        	self.render('cravel.html', destinations = destinations, trips = trips, questions = questions)
		
	def loadData(self):
		dest = Destination1(name = "Darjeeling", location = "India")
		dest.put()
		
		dest = Destination1(name = "Gangtok", location = "India")
		dest.put()

		dest = Destination1(name = "Sikkim", location = "India")
		dest.put()

		dest = Destination1(name = "Delhi", location = "India")
		dest.put()

		trip = Trip(name='Ujjals Trip to Goa', user_name = 'ujjal', user_id = '1', destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')])
		trip.put()
		
		trip = Trip(name='Weekend trip near Kolkata', user_name = 'ujjal', user_id = '1', destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')])
		trip.put()

		trip = Trip(name='Gateway from Kolkata', user_name = 'ujjal', user_id = '1', destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')])
		trip.put()

		trip = Trip(name='Honeymoon on the Himalayas', user_name = 'ujjal', user_id = '1', destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')])
		trip.put()

		question = Question(question='What is the best place to near Kolkata', user_name = 'ujjal', user_id = '1', answers = Answer(destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')]))
		question.put()
		
		question = Question(question='What is the best place to near Delhi', user_name = 'ujjal', user_id = '1', answers = Answer(destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')]))
		question.put()

		question = Question(question='What is the best place to near Bangalore', user_name = 'ujjal', user_id = '1', answers = Answer(destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')]))
		question.put()

		question = Question(question='What is the best place to near Mumbai', user_name = 'ujjal', user_id = '1', answers = Answer(destinations = [Destination1(name='Kolkata', location='India'), Destination1(name='Durgapur', location='India')]))
		question.put()



class NewQuestion(BlogHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('question-edit.html', q = None)

    def post(self):
        global db_timer
        if not self.user:
            self.redirect('/')

        question = self.request.get('question')
        logging.error('NewQuestion.post question:'+question)
        qurl = question.replace(' ','-')
        logging.error('NewQuestion.post qurl:'+qurl)

        if question:
            q = Question(question = question, qurl = '/'+qurl)
            q = q.put()
            self.redirect('/%s' % qurl)
            
        else:
            error = "question, please!"
            self.render("question.html", question=question, error=error)
            

class NewTrip(BlogHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('trip-edit.html', t = None)

    def post(self):
        global db_timer
        if not self.user:
            self.redirect('/')

        tname = self.request.get('tname')
        logging.error('NewTrip.post tname:'+tname)
        turl = tname.replace(' ','-')
        logging.error('NewQuestion.post turl:'+turl)

        if tname:
            t = Trip(name = tname, turl = '/'+turl)
            t = t.put()
#            logging.error(t)
            self.redirect('/%s' % turl)
            
        else:
            error = "trip, please!"
            self.render("trip-edit.html", t=trip, error=error)

class NewDestination(BlogHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('destination-edit.html', d = None)

    def post(self):
        global db_timer
        if not self.user:
            self.redirect('/')

        dname = self.request.get('dname')
        dlocation = self.request.get('dlocation')
        description = self.request.get('description')
        details = self.request.get('details')
        
        logging.error('NewDestination.post dname:'+dname)
        durl = dname.replace(' ','-')
        logging.error('NewDestination.post durl:'+durl)

        if dname:
            d = Destination1(name = dname, durl = '/'+durl, description = description, location = dlocation)
            d = d.put()
#            logging.error(t)
            self.redirect('/%s' % durl)
            
        else:
            error = "destination, please!"
            self.render("destination-edit.html", t=trip, error=error)

class CravelPage(BlogHandler):
   
   def get(self, npath=''):
        user_id = self.read_secure_cookie('user_id')
        
        version = self.request.get('v')
        
        path = self.request.path
        qpath = path + '?'
        logging.error('CravelPage.get - path:'+qpath)

	questionQuery = Question.getQuestionByPath(qpath)
        #logging.error(questionQuery)
        if questionQuery and questionQuery.count() > 0:
        #	logging.error('count > 0')
        	question = questionQuery.fetch()
        #	logging.error(question)
        	#BlogHandler.render()#
        	self.render('cravel-page.html', question = question[0], view=True)
    	else:
		tripQuery = Trip.getTripByPath(path)
		if tripQuery and tripQuery.count() > 0:
			trip = tripQuery.fetch()
			self.render('cravel-page.html', trip = trip[0])
		else:
			destQuery = Destination1.getDestinationByPath(path)
			if destQuery and destQuery.count() > 0:
				dest = destQuery.fetch()
				logging.error(dest[0])
				self.render('cravel-page.html', dest = dest[0], view=True)
			else:
				self.redirect('/error')
	    		
	    		
	    	
    
   def post(self, path):
   	answer = self.request.get('answer')
   	destinations = self.request.get('destinations')
   	destinationList = destinations.split(',')
   	if answer or destinationList:
   		qQuery = Question.getQuestionByPath(path+'?')
   		if qQuery and qQuery.count() >= 1:
   			question = qQuery.fetch()
   			#version = wiki.version
   			#version = version + 1
   			d = []
			for dest in destinationList:
				dest = Destination1.getDestinationByName(dest)
				d.append(dest.fetch()[0].key)
								
   			ans = Answer(ansText = answer)
   			ans.destinations = d
   			ans.put()
   			
   			question[0].answers.append(ans.key)
   			question[0].put()

	self.redirect(path)
    
    	
            
class Error(BlogHandler):
	def get(self):
		self.write('error')

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

	
app = webapp2.WSGIApplication([#('/', MainPage),
                               #('/unit2/rot13', Rot13),
                               #('/unit2/signup', Unit2Signup),
                               #('/unit2/welcome', Welcome),
                               #('/blog/?', BlogFront),
                               #('/blog/([0-9]+)', PostPage),
                               #('/blog/newpost', NewPost),
                               #('/blog/.json', Json),
                               #('/blog/([0-9]+).json', PermJson),
                               #('/flush', Flush),
                               #('/unit3/welcome', Unit3Welcome),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
			       #('/question' + PAGE_RE, EditWiki),
			       #('/_history' + PAGE_RE, HistoryWiki),
                               ('/', Cravel),
                               ('/question', NewQuestion),
                               ('/trip', NewTrip),
                               ('/destination', NewDestination),
                               ('/error', Error),
                               (PAGE_RE, CravelPage),
                               ],
                              debug=True)
