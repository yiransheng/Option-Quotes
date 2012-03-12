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
import defs


    
class MainPage(request.WebPageHandler):
    def get(self):
        stocks = Stock.get_all()
        template_values = {
            'title': defs.APP_NAME,
            'external': OPTIONS_CHAIN_HTML,
            'stocks': stocks,
        }
        
        self.response.out.write(self.render_template('site.html', \
                                                      template_values))
        
class CsvGen(request.WebPageHandler):
    def get(self):
        symbol = self.request.get('symbol')
        start = self.request.get('start')
        end = self.request.get('end')
        startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date() \
                        if start else datetime.date(1990,12,4)
        enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date() \
                  if end else datetime.datetime.now().date()
        options = OptionData.get_all_symbol(symbol) if symbol else None
        if not options:
            return False
        csvlines = ["date,symbol,underlying,contractname,type,strike,last,change,bid,ask,volume,openinterest"]
        for option in options:
            if option.date >=startdate and option.date<=enddate:
                csvlines.append(option.data)

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
