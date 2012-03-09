import datetime
import sys
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
import urllib2

###########
from models import *

class MainPage(webapp.RequestHandler):
    def get(self):
        stock = Stock.get('BAC')
        if stock:            
            print('here i am')
        else:
            print('it is new')
            stock = Stock(symbol='BAC')
            stock.put()
        url = stock.cboe_query_gen()
        jsontxt = self.fetch_json(url)
        print(simplejson.loads(jsontxt)["options"])
        self.format_data(jsontxt, 'BAC', None)
        
    def fetch_json(self, url):
        try:
            option_json = urllib2.urlopen(url)
            # return simplejson.loads(option_json.read())
            return option_json.read()
        except urllib2.URLError, e:
            handleError(e)
            
    def format_data(self, jsontxt, symbol, expiration):
        options_raw = simplejson.loads(jsontxt)["options"]
        for type in [u"calls",u"puts"]:
            for call in options_raw[type]:
                i = options_raw[type].index(call)                
                contractname = call[0]
                try:
                    last = float(call[1])
                except:
                    last = -1.0
                try:
                    change = float(call[2])
                except:
                    change = -1.0
                try:
                    bid = float(call[3])
                except:
                    bid = -1.0
                try:
                    ask = float(call[4])
                except:
                    ask = -1.0
                try:
                    volume = int(call[5])
                except:
                    volume = -1
                try:
                    openinterest = int(call[6])
                except:
                    openinterest = -1
                try:
                    underlying = float(options_raw[u"uprice"])
                except:
                    underlying = -1.0
                try:
                    strike = float(options_raw[u"strikes"][i])
                except:
                    strike = -1.0

                option = Option(symbol=symbol, 
                                # expiration = expiration, 
                                type = type, 
                                contractname = contractname, 
                                strike = strike, 
                                last = last, 
                                change = change, 
                                bid = bid, 
                                ask = ask, 
                                volume = volume,
                                openinterest = openinterest,
                                underlying = underlying)

                option.put()

                    
                
        

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
