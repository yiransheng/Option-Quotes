"""
Base class for requests 
"""

import os
import datetime
import sys
from google.appengine.api import urlfetch
import urllib2

from BeautifulSoup import BeautifulSoup 
from django.utils import simplejson


from models import *

# -----------------------------------------------------------------------------
# Query Destinations & Constants
# -----------------------------------------------------------------------------
DATA_SRC = 'http://delayedquotes.cboe.com'
SYMBOL_LOOKUP_URL = 'http://delayedquotes.cboe.com/new/www/symbol_lookup.html?symbol_lookup='
OPTIONS_CHAIN_HTML = 'http://delayedquotes.cboe.com/new/options/options_chain.html?'
OPTIONS_CHAIN_JSON = 'http://delayedquotes.cboe.com/json/options_chain.html?'
# -----------------------------------------------------------------------------
# Patch & Extend appengine fetch api's deadline time
# -----------------------------------------------------------------------------
old_fetch = urlfetch.fetch
def new_fetch(url, payload=None, method=urlfetch.GET, headers={},
          allow_truncated=False, follow_redirects=True,
          deadline=600, *args, **kwargs):
  return old_fetch(url, payload, method, headers, allow_truncated,
                   follow_redirects, deadline, *args, **kwargs)
urlfetch.fetch = new_fetch


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class Cboe:
    def __init__(self, symbol, \
                 idLookup=False, \
                 expirationLookup=False, \
                 stock=None):
        if stock:
            self.stock=stock
        else:
            self.stock = Stock(symbol=symbol)
        if idLookup:
            self.symbol_lookup()
        if expirationLookup:
            self.expiration_lookup()

    def symbol_lookup(self):
        """
        Lookup a stock symbol, and get the ID_NOTATION, ID_OSI, ASSET_CLASS parameters.
        """
        try: 
            url = SYMBOL_LOOKUP_URL + self.stock.symbol
            result = urllib2.urlopen(url).url
            cboe_id = result.split("?")[1]
            self.stock.cboe_id = cboe_id
        except urllib2.URLError, e:
            cboe_id = ""

        return cboe_id

    def json_lookup(self, expiration=None):
        """
        Lookup the json format option chain for a given expiration month, and
        convert it to a Option model
        """
        if expiration:
            expiration_str =  expiration.strftime('%Y%m')
        cboe_id = self.stock.cboe_id if self.stock.cboe_id else self.symbol_lookup()
        url = "".join([OPTIONS_CHAIN_JSON,cboe_id,"&expirationdate=",expiration_str])
        try:
            option_jsontxt = urllib2.urlopen(url).read()
            return option_jsontxt
        except urllib2.URLError, e:
            return False
          
    def json_to_option(self, option_jsontxt):
        if not option_jsontxt:
            return False
        options_raw= simplejson.loads(option_jsontxt)["options"]
        options = []
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

                option = Option(symbol=self.stock.symbol, 
                                expiration = expiration, 
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
                options.append(option)

        return options

    
    def expiration_lookup(self):
        """
        Lookup all avaiable expiration months
        """
        cboe_id = self.stock.cboe_id if self.stock.cboe_id else self.symbol_lookup()
        url = "".join([OPTIONS_CHAIN_HTML,cboe_id])
        try:
            option_html = urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            return None

        soup = BeautifulSoup(option_html)
        select = soup.findAll('select', attrs = {"name" :"expirationdate" })
        exp_months= []
        for t in select[0].contents:
            try:
                exp_months.append(datetime.datetime.strptime(t.string, '%b %Y').date())
            except:
                pass 

        self.stock.exp_months = exp_months
        
        return exp_months
    def json_to_csv(self, option_jsontxt, expdate, settings = \
                            {'dateformat' : '%Y-%m-%d',
                             'expformat' : '%Y-%m',
                             'na': 'NA',
                              'sep': ','
                             }):
        symbol = self.stock.symbol
        now = datetime.datetime.now()
        today = now.date()
        date = today.strftime(settings['dateformat'])
        expiration = expdate.strftime(settings['expformat'])
        options_raw= simplejson.loads(option_jsontxt)["options"]
        options_csv = []
        for type in [u"calls",u"puts"]:
            for call in options_raw[type]:
                i = options_raw[type].index(call)                
                contractname = call[0]
                try:
                    last = str(float(call[1]))
                except:
                    last = settings['na']
                try:
                    change = str(float(call[2]))
                except:
                    change = settings['na']
                try:
                    bid = str(float(call[3]))
                except:
                    bid = settings['na']
                try:
                    ask = str(float(call[4]))
                except:
                    ask = settings['na']
                try:
                    volume = str(int(call[5]))
                except:
                    volume = settings['na']
                try:
                    openinterest = str(int(call[6]))
                except:
                    openinterest = settings['na']
                try:
                    underlying = str(float(options_raw[u"uprice"]))
                except:
                    underlying = settings['na']
                try:
                    strike = str(float(options_raw[u"strikes"][i]))
                except:
                    strike = settings['na']

                option_csv = settings['sep'].join([date, symbol, underlying, contractname, \
                                 type, strike, last, change, bid, ask, volume, \
                                 openinterest])
                options_csv.append(option_csv)

        return "\n".join(options_csv)
                
    def option_chain_store(self):
        """
        Store the option chains for all expirations
        """
        if not self.stock.exp_months:
            self.expiration_lookup()
            
        for expdate in self.stock.exp_months:            
            option_jsontxt = self.json_lookup(expdate)
            if not option_jsontxt:
                return False
            else:
                options_csv = self.json_to_csv(option_jsontxt, expdate)
            today = datetime.datetime.now().date()
            day = today.strftime("%Y%m%d")
            exp = expdate.strftime("%Y%m")
            id = self.stock.symbol + day + exp
            previous = OptionData.get(id)
            if previous:
                previous.data = options_csv
                previous.put()
                return True
            else: 
                try:    
                    optionData = OptionData(symbol = self.stock.symbol,
                                    expiration = expdate,
                                    data = options_csv,
                                    id = id)
                    optionData.put()
                except:
                    return False

            
            
            
        
        
        
