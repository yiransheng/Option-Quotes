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

def tocsv(option, settings = {'dateformat' : '%Y-%m-%d',
                             'expformat' : '%Y-%m',
                             'na': 'NA',
                              'sep': ','
                             }):
    symbol = option.symbol
    date = option.date.strftime(settings['dateformat'])
    expiration = option.expiration.strftime(settings['expformat'])
    type = option.type
    contractname = option.contractname
    strike = str(option.strike) if option.strike>0 else settings['na']
    last = str(option.last) if option.last>0 else settings['na']
    change = str(option.change) if option.change>0 else settings['na']
    bid = str(option.bid) if option.bid>0 else settings['na']
    ask = str(option.ask) if option.ask>0 else settings['na']
    underlying = str(option.underlying) if option.underlying>0 else settings['na']
    volume = str(option.volume) if option.volume>0 else settings['na']
    openinterest = str(option.openinterest) if option.openinterest>0 else settings['na']

    return settings['sep'].join([date, symbol, underlying, contractname, \
                                 type, strike, last, change, bid, ask, volume, \
                                 openinterest])
    
class MainPage(request.WebPageHandler):
    def get(self):
        stocks = Stock.get_all()
        for stock in stocks:
            pass
        
class CsvGen(request.WebPageHandler):
    def get(self):
        symbol = self.request.get('symbol')
        start = self.request.get('start')
        end = self.request.get('end')
        startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date() \
                        if start else datetime.date(1990,12,4)
        enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date() \
                  if end else datetime.datetime.now().date()
        options = Option.get_all_symbol(symbol) if symbol else None
        if not options:
            return False
        csvlines = ["date,symbol,underlying,contractname,type,strike,last,change,bid,ask,volume,openinterest"]
        for option in options:
            if option.date >startdate and option.date<enddate:
                csvlines.append(tocsv(option))

        csvfile = "\n".join(csvlines)
        self.response.headers['Content-Type'] = 'application/csv'
        self.response.headers['Content-Disposition'] = 'attachment; filename='+symbol+'.csv'
        self.response.out.write(csvfile)
                
        

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/csv/?$', CsvGen)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
