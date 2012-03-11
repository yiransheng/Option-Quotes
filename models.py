import datetime
import sys
import urllib2

from google.appengine.ext import db


FETCH_THEM_ALL = 65535

class Option(db.Model):

    symbol = db.StringProperty(required=True)
    date = db.DateProperty(required=True, auto_now_add=True)
    expiration = db.DateProperty()
    type = db.StringProperty(required=True, choices=set([u"calls",u"puts"]))
    contractname = db.StringProperty()
    strike = db.FloatProperty()
    last = db.FloatProperty()
    change = db.FloatProperty()
    bid = db.FloatProperty()
    ask = db.FloatProperty()
    underlying = db.FloatProperty()
    volume = db.IntegerProperty()
    openinterest = db.IntegerProperty()       

    @classmethod
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    @classmethod
    def get_all(cls):
        q = db.Query(Option)
        q.order('-date')
        return q.fetch(FETCH_THEM_ALL)
    @classmethod
    def get_all_symbol(cls, symbol):
        q = db.Query(Option)
        q.filter('symbol = ', symbol)
        q.order('-date')
        return q.fetch(FETCH_THEM_ALL)
    @classmethod
    def get(cls, symbol, date, expiration):
        q = db.Query(Option)
        q.filter('symbol = ', symbol)
        q.filter('date = ', date)
        q.filter('expiration = ', expiration)
        return q.fetch(FETCH_THEM_ALL)
        
        
    

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return '[%s] %s' %\
               (self.date.strftime('%Y/%m/%d'), self.contractname)

class Stock(db.Model):

    symbol = db.StringProperty(required=True)
    cboe_id = db.StringProperty()
    exp_months = db.ListProperty(datetime.date)


    @classmethod
    def get_all(cls):
        q = db.Query(Stock)
        return q.fetch(FETCH_THEM_ALL)
    @classmethod
    def get(cls,symbol):
        q = db.Query(Stock)
        q.filter('symbol = ', symbol)
        return q.get()
