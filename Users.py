from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
import hmac
import hashlib
import random
from string import letters

secret = 'fart'


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
    return ndb.Key('users', group)


class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        uquery = User.get_by_id(uid, users_key())
        logging.error('***by_id****%s' % uquery)
        #uquery = User.query().filter(User. == uid)
        return uquery

    @classmethod
    def by_name(cls, name):
        #u = User.all().filter('name =', name).get()
        uquery = User.query().filter(User.name == name)
        return uquery

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
        #logging.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s' % u)
        if u:
        	u = u.fetch()[0]
        #	logging.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s' % u)
        	if u and valid_pw(name, pw, u.pw_hash):
        	    return u
