"""
Base class for requests 
"""

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

import defs

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class WebPageHandler(webapp.RequestHandler):
    def get_template(self, template_name):
        return os.path.join(os.path.dirname(__file__), 
                            defs.TEMPLATE_SUBDIR,
                            template_name)

    def render_template(self, template_name, template_vars):
        template_path = self.get_template(template_name)
        return template.render(template_path, template_vars)
        

    
