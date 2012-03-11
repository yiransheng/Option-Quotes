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
        template_values = {
            'greetings': 'greetings',
            'stocks': stocks,
        }
        
        self.response.out.write(self.render_template('base.html', \
                                                      template_values))
class ModifyStockInfo(request.WebPageHandler):
    def post(self):
        symbol = self.request.get('symbol')
        action = self.request.get('action')
        if action == '2':
            self.update_all()
            self.redirect('/admin/')
            
        if action == '1':
            cboeQuery = Cboe(symbol, True, True)
            stock = Stock.get(cboeQuery.stock.symbol)
            if stock:
                stock.cboe_id = cboeQuery.stock.cboe_id
                stock.exp_months = cboeQuery.stock.exp_months
            else:
                stock = cboeQuery.stock
            stock.put()
            self.redirect('/admin/')
            
    def update_all(self):
        stocks = Stock.get_all()
        for stock in stocks:
            cboeQuery = Cboe(stock.symbol, True, True)
            stock.cboe_id = cboeQuery.stock.cboe_id
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
