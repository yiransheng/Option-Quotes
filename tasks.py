import datetime
import sys
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
import urllib2

###########
from models import *
from queries import *
import request 

    
class MainTask(request.WebPageHandler):
    def get(self):
        stocks = Stock.get_all()
        for stock in stocks:
            cboeQuery = Cboe('', False, False, stock)
            cboeQuery.option_chain_store()
        
                
        

application = webapp.WSGIApplication(
                                     [('/tasks/main/?', MainTask)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
