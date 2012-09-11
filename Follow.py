from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
import hmac
import hashlib
import random
from string import letters
from Base import *

def follows_key(group = 'default'):
    return ndb.Key('follows', group)

class Follow(ndb.Model):
    name = ndb.StringProperty(required = True)	
    uurl = ndb.StringProperty(required = True)
    ukey = ndb.KeyProperty(required = True)
    search_name = ndb.StringProperty(required = True)
    comment = ndb.StringProperty(repeated=True)
    
    created = ndb.DateTimeProperty(auto_now_add = True)
    lastModified = ndb.DateTimeProperty(auto_now = True)

    def _pre_put_hook(self):
	self.search_name = self.name.upper()

    def render(self, view=False):
	    logging.error('in User render')
	   # self._render_text = self.content.replace('\n', '<br>')
	    return render_jinja_str("cravel-content-user-follows.html", f = self, view=view)

    @classmethod
    def getAllUsersIAmFollowing(self):
        follow_entity = Follow.get_by_id(fid, follows_key())
        return user_entity
    
    @classmethod
    def follow_a_person(self, name, uurl, ukey):
        return Follow(parent = follows_key(),
                    name = name,
                    ukey = ukey,
                    uurl = uurl)
    
    	
