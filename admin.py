import datetime
import sys

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
import urllib2

###########
from models import *
from queries import *
import request 

class MainPage(request.WebPageHandler):
    def get(self):
        stocks = Stock.get_all()
        template_values = {
            'greetings': 'greetings',
            'stocks': stocks,
            'url_linktext': 'No',
        }
        
        self.response.out.write(self.render_template('base.html', \
                                                      template_values))
class ModifyStockInfo(request.WebPageHandler):
    def get(self):
        pass
    def update_all():
        stocks = Stock.get_all()
        for stock in stocks:
            cboeQuery = Cboe(stock.symbol, True, True)
            stock.cboe_id = cboeQuery.stock.cobe_id
            stock.exp_months = cboeQuery.stock.exp_months
            stock.put()

application = webapp.WSGIApplication(
                                     [('/admin/*$', MainPage),
                                      ('/admin/modify/*$', ModifyStockInfo),
                                      ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
