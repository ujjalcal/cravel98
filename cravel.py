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
from cutil import striplist

import webapp2
import jinja2
import oembed

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
      
      	#logging.error(params)
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
    	#logging.error(user.key)
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        logging.error('****initialize***%s' % uid)
        self.user = uid and User.by_id(int(uid))
        #logging.error('*******%s' % self.user)
        
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
        logging.error('@@@@@##### %s' % u)
        logging.error('@@@@@##### %s' % u.count())
        if u and u.count()>0:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
	    uurl = "/user/"+self.username
            u = User.register(self.username, self.password, uurl, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Login(BlogHandler):
    def get(self):
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
	
	        user_id = self.read_secure_cookie('user_id')
        	
	        search = self.request.get('search')
	        logging.error('search:'+search)
	        
	        if search:
	        	destinations = Destination1.getDestinationByName(search)
		else:	
			destinations = Destination1.getAllDestinations().fetch(10)
			
		if search:
			trips = Trip.getTripByName(search)
		else:	
			trips = Trip.getAllTrips().fetch(10)
		
		if search:
			questions = Question.getQuestionByName(search)
		else:	
			questions = Question.getAllQuestions().fetch(10)

        	self.render('cravel.html', destinations = destinations, trips = trips, questions = questions)
		

class QuestionHandler(BlogHandler):
    def create_update_question(self):
        global db_timer
        if not self.user:
            self.redirect('/')

	ukey = self.user.key
        question = self.request.get('question').strip()
        question = question if question[-1:] == '?' else question+'?'
        
        #logging.error('NewQuestion.post question:'+question)
        #### form the url###
        new_question = re.sub('[^a-zA-Z0-9\n\.]', '', question)
	new_question = new_question[:-1]+'?'
        qurl = 'qs/'+new_question.replace(' ','-')
        
        logging.error('NewQuestion.post qurl:'+qurl)

        path = self.request.path
	isEdit = True if path[:6] == '/_edit' else False
	path = path[6:]+'?' if isEdit else path+'?'
	
	logging.error('NewQuestion.post path:'+path)
	logging.error(isEdit)
        if question:
	    qq = Question.getQuestionByPath(path)
	    logging.error(qq.count())
	    if qq and qq.count()>0:
	    	q = qq.fetch()[0]
	    	q.last_updated_by = ukey
	    else:
	    	q = Question()
	    	q.added_by = ukey
	    	
            q.question = question
            q.qurl = '/'+qurl
            
            q = q.put()
            self.redirect('/%s' % qurl)
            
        else:
            error = "question, please!"
            self.render("question.html", q=question, error=error)
    

class NewQuestion(QuestionHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('question-edit.html', q = None)

    def post(self):
        self.create_update_question()

class EditQuestion(QuestionHandler):
   
   def get(self, npath=''):
        user_id = self.read_secure_cookie('user_id')
        if not user_id:
        	self.redirect('/login')
        
        version = self.request.get('v')
        
        pathWithEdit = self.request.path
        path = pathWithEdit[6:]
        qpath = path + '?'
        logging.error('CravelPage.get - path:'+qpath)

	questionQuery = Question.getQuestionByPath(qpath)
        if questionQuery and questionQuery.count() > 0:
        	question = questionQuery.fetch()
        	self.render('question-edit.html', q = question[0], view=True)
	else:
		self.redirect('/error')
	    		

   def post(self, path):
	self.create_update_question()   


class TripHandler(BlogHandler):

    def create_update_trip(self):
        global db_timer
        if not self.user:
            self.redirect('/')

        ukey = self.user.key
        tname = self.request.get('tname')
        tdescription = self.request.get('tdescription')
        tdetails = self.request.get('tdetails')
        tlinks = self.request.get('tlinks')
        linkList = striplist(tlinks.split(','))
        ttags = self.request.get('ttags')
	taglist = striplist(ttags.split(','))
	
        tdestinations = self.request.get('tdestinations').strip()
        d = []
        destinationList = striplist(tdestinations.split(','))
        if len(destinationList)>0:
		for dest in destinationList:
			#TODO add exception handling - trim spaces
			dest = Destination1.getDestinationByName(dest.strip())
			logging.error(dest.count())
			if dest and dest.count() > 0:
				d.append(dest.fetch()[0].key)

        #logging.error('NewTrip.post tname:'+tname)
        turl = 'trip/'+tname.replace(' ','-')

        path = self.request.path
	isEdit = True if path[:6] == '/_edit' else False
	path = path[6:] if isEdit else path

		
        logging.error('NewTrip.post turl:'+turl)
	
        if tname:
	    tq = Trip.getTripByPath(path)	
    	    if tq and tq.count()>0:
		t = tq.fetch()[0]
		t.last_updated_by = ukey
	    else:
	        t = Trip()
	        t.added_by = ukey
	    
	    t.name = tname
	    t.turl = '/'+turl
	    t.description=tdescription
	    t.details=tdetails
	    t.destinations = d
	    t.tags = taglist
	    t.links=linkList
	    
            t = t.put()
            self.redirect('/%s' % turl)
            
        else:
            error = "trip, please!"
            self.render("trip-edit.html", t=trip, error=error)



class NewTrip(TripHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('trip-edit.html', t = None)

    def post(self):
    	self.create_update_trip()

class EditTrip(TripHandler):
   
   def get(self, npath=''):
        user_id = self.read_secure_cookie('user_id')
        
        if not user_id:
        	self.redirect('/login')
        version = self.request.get('v')
        
        pathWithEdit = self.request.path
        path = pathWithEdit[6:]

	tripQuery = Trip.getTripByPath(path)
	if tripQuery and tripQuery.count() > 0:
		trip = tripQuery.fetch()
		self.render('trip-edit.html', t = trip[0], view=True, user=None)
	else:
		self.redirect('/error')
	    		
	    		
	    	
   
   ##Posting new Answer for a Question
   def post(self, path):
	self.create_update_trip()
	
	
class DestinationHandler(BlogHandler):

    def create_update_destination(self):
        global db_timer
        if not self.user:
            self.redirect('/')
        ukey = self.user.key
        
        path = self.request.path
#	logging.error('%%%%%%%%%%%%%'+path[:6])
#	logging.error(path)
	isEdit = True if path[:6] == '/_edit' else False
	path = path[6:] if isEdit else path
#	logging.error(path)
#	logging.error(isEdit)
        dname = self.request.get('dname')
        dlocation = self.request.get('dlocation')
        description = self.request.get('description')
        details = self.request.get('details')
        videos = self.request.get('videos').split(',')
        pictures = self.request.get('pictures').split(',')
        map = self.request.get('map')

#        #logging.error('NewDestination.post dname:'+dname)
        durl = 'destination/'+dname.replace(' ','-')
#        logging.error('NewDestination.post durl:'+durl)

        if dname:
            dq = Destination1.getDestinationByPath(path)
#            logging.error("@@@@@@@@@@@@@@@@@@@@@@@")
#            logging.error(dq.count())
            
            if dq and dq.count()>0:
            	d = dq.fetch()[0]
                d.last_updated_by = ukey
            else:
            	d = Destination1()
            	d.added_by = ukey

            d.name = dname
            d.durl = '/'+durl
            d.description = description
            d.location = dlocation
            d.details = details
            d.videos = videos
            d.pictures = pictures
            d.map = map
            
#           d = Destination1(name = dname, durl = '/'+durl, description = description, location = dlocation, details = details, added_by = ukey, videos = videos, pictures = pictures, map = map)
            
            d = d.put()
#           logging.error(t)
            self.redirect('/%s' % durl)
            
        else:
            error = "destination, please!"
            self.render("destination-edit.html", t=trip, error=error)
    	
class NewDestination(DestinationHandler):
    def get(self):
        user_id = self.read_secure_cookie('user_id')
        version = self.request.get('v')
        
        if not user_id:
        	self.redirect('/login')
        	
   	self.render('destination-edit.html', d = None)

    def post(self):
	self.create_update_destination()

class EditDestination(DestinationHandler):
   
   def get(self, npath=''):
        user_id = self.read_secure_cookie('user_id')
        
        if not user_id:
        	self.redirect('/login')
        version = self.request.get('v')
        
        pathWithEdit = self.request.path
        path = pathWithEdit[6:]

	destQuery = Destination1.getDestinationByPath(path)
	if destQuery and destQuery.count() > 0:
		dest = destQuery.fetch()
		#logging.error(dest[0])
		self.render('destination-edit.html', d = dest[0], view=True)
	else:
		self.redirect('/error')
	    		
   ##Updating a Destination
   def post(self, path):
	self.create_update_destination()   


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
			self.render('cravel-page.html', trip = trip[0], view=True, user=None)
		else:
			destQuery = Destination1.getDestinationByPath(path)
			if destQuery and destQuery.count() > 0:
				dest = destQuery.fetch()
				logging.error("#############user###############")
				logging.error(dest)
				self.render('cravel-page.html', dest = dest[0], view=True)
			else:
				userQuery = User.getUserByPath(path)
				
				if userQuery and userQuery.count() > 0:
					user = userQuery.fetch()
					#logging.error(dest[0])
					self.render('cravel-page.html', u = user[0], view=True)
				else:
					self.redirect('/error')
	    		
	    		
	    	
   
   ##Posting new Answer for a Question
   def post(self, path):
   
        if not self.user:
            self.redirect('/')

        ukey = self.user.key
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
   			t = []
			for dest in destinationList:
				dest = Destination1.getDestinationByName(dest.strip())
				logging.error("!!!!!!!!!!!!!!")
				logging.error(dest.count())
				if dest and dest.count()>0:
					d.append(dest.fetch()[0].key)
					
			for tripStr in destinationList:
				trip = Trip.getTripByName(tripStr.strip())
				logging.error("!!!!!!!!!!!!!!")
				logging.error(trip.count())
				if trip and trip.count()>0:
					t.append(trip.fetch()[0].key)
								
   			ans = Answer(ansText = answer, added_by=ukey)
   			ans.destinations = d
   			ans.trips = t
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
			       #('/_history' + PAGE_RE, HistoryWiki),
                               ('/', Cravel),
                               ('/question', NewQuestion),
                               ('/trip', NewTrip),
                               ('/destination', NewDestination),
                               ('/error', Error),
			       ('/_edit/destination' + PAGE_RE, EditDestination),
			       ('/_edit/trip' + PAGE_RE, EditTrip),
			       ('/_edit/qs' + PAGE_RE, EditQuestion),
                               (PAGE_RE, CravelPage),
                               ],
                              debug=True)
