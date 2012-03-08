from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson 
import urllib2

###########
from models import *

class MainPage(webapp.RequestHandler):
    def get(self):
        stock = Stock(symbol='AAPL')
        stock.put()
        print('OK')
        url = stock.cboe_query_gen()
        print(url)
        
    def fetch_json(self, rpc_url):
        try:
            option_json = urllib2.urlopen(rpc_url)
            return simplejson.loads(option_json.read())
        except urllib2.URLError, e:
            handleError(e)
        

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
