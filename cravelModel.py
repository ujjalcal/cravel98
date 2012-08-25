from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)
    
    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d

    @classmethod
    def permalink(self, post_id):
        #key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        #post = db.get(key)
    	posts = list(self.allPosts())
    	for post in posts:
    		if post.key().id() == int(post_id):
        		return post
	
    @classmethod
    def allPosts(self, update=False):
    	key = 'top'
    	posts = memcache.get(key)
    	
    	if posts is None or update:
    		logging.error('DB Query')
    		posts = Post.all().order('-created')
    		#posts = list(posts)
    		memcache.set(key, posts)
	else:
		logging.error('No DB Query')
    
    	return posts

########################################

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

###################################

class Answer(ndb.Model):
	destinations = ndb.StructuredProperty(Destination1, repeated = True)
	trips = ndb.StructuredProperty(Trip)

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
	
	
	def render(self):
	    logging.error('in Answer render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_str("cravel-content-answer.html", a = self)


####################################

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
	    return render_str("cravel-content-trip.html", t = self)

	
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
    		
#####################################

class Destination1(ndb.Model):
	name = ndb.StringProperty()
	location = ndb.StringProperty()
	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
	
	def render(self):
	    logging.error('in Destination render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_str("cravel-content.html", d = self)

	
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


#######################################

class Question(ndb.Model):
	question = ndb.StringProperty()
	answers = ndb.StructuredProperty(Answer)

	user_name = ndb.StringProperty()
	user_id = ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)
	lastModified = ndb.DateTimeProperty(auto_now = True)
		
	def render(self):
	    logging.error('in Question render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_str("cravel-content-question.html", q = self)

	
	@classmethod
	def getQuestionByName(self, question):
		questions = Question.query().filter(Question.question == question)
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
