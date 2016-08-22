#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from mongoengine import *
from hcrawler_models import Hprice, Hentity
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
from hprice_cleaning import HpriceCleansing
DB = 'hcrawler'
connect(db = DB, host='localhost:27017', username = 'hcrawler', password = 'f#d1p9c')

print ('connect finished')

def url2domain(url):
    from urlparse import urlparse
    #url = 'http://user:pass@example.com:8080'
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    domain = re.sub("^.+@","",domain)
    domain = re.sub(":.+$","",domain)
    return domain

class KmzyCleansing(HpriceCleansing):
    def parse_single_item(self, item):
        mongo_item = Hprice()
        mongo_item.productGrade = item[u'specs'].split('/')[0]
        mongo_item.priceCurrency = 'CNY'                        # 价格货币，命名规则使用iso-4217
        mongo_item.confidence = "0.7"                            # 爬取日期
        mongo_item.productPlaceOfOrigin = item[u'specs'].split('/')[1]        # 原产地
        mongo_item.source = item[u'source']                       # 数据源url

        mongo_item.name = item[u'name']
        name_raw = item[u'name'] 
        mongo_item.mainEntityOfPage = self.nameMapper.get(name_raw, name_raw)
        mongo_item.nid = self.get_nid(name_raw)         
        mongo_item.site = url2domain(mongo_item.source)
        # del mongo_item.properties
        # print mongo_item.properties
        

        for mon, price in item['data']:
            mongo_item.validDate = mon
            mongo_item.price = str(price)
            self.counter +=1
            if not self.counter%100:
                print self.counter
            mongo_item.save()


    def get_nid(self, name):
        ret_list = Hentity.objects(alias__in=name)
        max_length = -1
        longest_ret = None
        for ret in ret_list:
            if len(ret['alias']) > max_length:
                max_length = len(ret['alias'])
                longest_ret = ret
        return longest_ret['nid']

if __name__ == '__main__':
    c = KmzyCleansing('kmzy-20160808')
    c.run()
                   
