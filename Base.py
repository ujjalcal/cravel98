import os
import webapp2
import jinja2
import logging


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_jinja_str(template, **params):
    logging.error(params)
    t = jinja_env.get_template(template)
    return t.render(params)


#def render_str_base(self, template, **params):
#    	#global db_timer
#        params['user'] = self.user
#        params['curr_time'] = round(time.time() - db_timer)
#        params['path'] = self.request.path
      
#        return render_str_final(template, **params)

##before actual writing inject prams##
#def render(self, template, **kw):
#        self.write(self.render_str(template, **kw))
