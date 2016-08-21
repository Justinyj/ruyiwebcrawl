#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from mongoengine import *
from hcrawler_models import Hprice, Hentity
from hprice_cleaning import HpriceCleansing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DB = 'admin'
connect(db = DB, host='localhost:27017', username = 'hcrawler', password = 'f#d1p9c')

print ('connect finished')
class CngrainCleansing(HpriceCleansing):
    def parse_single_item(self, item):
        for product in item['product_list']:
            if not product[u'price_history']:
                return
            else:
                for k,v in product[u'price_history'].iteritems():
                    #经试验，mongoenginee有类似python引用机制的地方，会产生覆盖，必须每次重新生成对象，暂时找不到其他解决方法
                    mongo_item = Hprice()
                    mongo_item.productGrade = product[u'level'] 
                    mongo_item.priceCurrency = 'CNY'
                    mongo_item.confidence = '0.7'
                    mongo_item.productPlaceOfOrigin = product['produce_area']       
                    mongo_item.source = item[u'source']        
                    mongo_item.productionYear = product[u'produce_year']                         
                    mongo_item.unitText = u'元/吨'
                    mongo_item.name = product[u'variety']  
                    mongo_item.sellerMarket = item[u'market']  
                    mongo_item.priceType = product[u'price_type']
                    mongo_item.site = self.url2domain(item[u'source'])
                    
                    name = mongo_item.name
                    mongo_item.mainEntityOfPage = self.nameMapper.get(name, name)
                    mongo_item.nid = self.nids.get(name, None)
                    if not mongo_item.nid:
                        mongo_item.nid = self.get_nid(name)

                    mongo_item[u'validDate'] = k   #日期
                    mongo_item[u'price']     = v   #价格
                    if not self.counter % 100:
                        print self.counter
                    self.counter += 1
                    mongo_item.save()
    
    def get_nid(self, name):
        ret_list = Hentity.objects(alias__in = [name])
        if not ret_list:
            print name.encode('utf-8')
            self.nids[name] = name
            return name
        max_length = -1
        longest_ret = None
        for ret in ret_list:
            if len(ret['alias']) > max_length:
                max_length = len(ret['alias'])
                longest_ret = ret
        self.nids[name] = longest_ret['nid']#加入缓存，下次对于相同的name访问直接从nids里取
        return longest_ret['nid']

if __name__ == '__main__':
    s = CngrainCleansing('cngrain-20160817')
    s.run()
