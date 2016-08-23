#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from mongoengine import *
from hcrawler_models import Hmaterial, Hentity
import sys
import re
import json
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

class ChemnetCleansing(HpriceCleansing):
    def parse_single_item(self, item):
        if 'name' in item:
            return
        # print json.dumps(item, encoding='utf-8', ensure_ascii=False)
        mongo_item = Hmaterial()
        if len(item[u'用途']) > 0:
            mongo_item.description =  item[u'用途']
        mongo_item.confidence = "0.7"
        mongo_item.category = 'chemical'
        # print item[u'上游原料'], item[u'下游产品'] 
        if len(item[u'上游原料']) > 0:
            mongo_item.upstream_material = item[u'上游原料']      
        mongo_item.source = item[u'source']        
        if len(item[u'下游产品'] ) > 0:
            mongo_item.downstream_material = item[u'下游产品']    

        mongo_item.name = item[u'中文名称']
        name_raw = item[u'中文名称'] 
        mongo_item.mainEntityOfPage = self.nameMapper.get(name_raw, name_raw)
        mongo_item.nid = self.get_nid(name_raw)         
        mongo_item.site = url2domain(mongo_item.source) 
        # print json.dumps(item[u'详细信息'], encoding='utf-8', ensure_ascii=False)
        properties = {}
        for info in [u'物化性质', u'分子式', u'中文别名', u'英文名称', u'分子量']:
            if item[info]:
                properties[info] = item[info]
        if properties:
            mongo_item.properties = properties
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
    s = ChemnetCleansing('chem-20160728')
    s.run()
                         
