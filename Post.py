from google.appengine.ext import db
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
        return render_jinja_str("post.html", p = self)
    
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
