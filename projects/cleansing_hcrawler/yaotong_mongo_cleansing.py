#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from mongoengine import *
from hcrawler_models import Hprice, Hentity
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from hprice_cleaning import HpriceCleansing
DB = 'hcrawler'
connect(db = DB, host='localhost:27017')#, username = 'hcrawer', password = 'f#d1P9c')

print ('connect finished')
class YtyaocaiCleansing(HpriceCleansing):
    def parse_single_item(self, item):
        item_suit_schema = self.init_item_schema()
        item_suit_schema['productPlaceOfOrigin'] = item[u'info'][u'产地']
        item_suit_schema['source']  = item[u'source']
        item_suit_schema['unitText'] = u'元/千克'
        item_suit_schema['confidence'] = 0.7
        item_suit_schema['mainEntityOfPage_raw'] = item['name']
        item_suit_schema['productGrade'] = item[u'info'][u'规格'] 
        self.clean_item_schema(item_suit_schema)
        name_raw = item_suit_schema['mainEntityOfPage_raw']
        item_suit_schema['nid'] = self.nids.get(name_raw, self.get_nid(name_raw))
        for k,v in item[u'price_history'].iteritems():
            result_item = item_suit_schema.copy()
            result_item['validDate'] = k   #日期
            result_item['price']     = v   #价格
            result_item['id']  = result_item['name'] + '_' + result_item['validDate']

            mongo_result = self.get_mongo_item(result_item)

            properties = {
                    u"十二个月盈利比例" : item[u'info'][u"十二个月盈利比例"] ,
                    u"市净率" : item[u'info'][u"市净率"] ,
                    u"生产市值" : item[u'info'][u"生产市值"],
                    u"代码" : item[u'info'][u"代码"],
                    u"九个月盈利比例" : item[u'info'][u"九个月盈利比例"] ,
                    u"生长周期" : item[u'info'][u"生长周期"] ,
                    u"浮动市值" : item[u'info'][u"浮动市值"] ,
                    u"关注度" : item[u'info'][u"关注度"] ,
                    u"当前价格" : item[u'info'][u"当前价格"] ,
                    u"三个月盈利比例" : item[u'info'][u"三个月盈利比例"] ,
                    u"权重比" : item[u'info'][u"权重比"] ,
                    u"生长环境" : item[u'info'][u"生长环境"] ,
                    u"六个月盈利比例" : item[u'info'][u"六个月盈利比例"] ,
            }
            mongo_result.properties = properties
            self.counter +=1
            if not self.counter%100:
                print self.counter
            mongo_result.save()

    def get_mongo_item(self,es_item):
        mongo_result = Hprice()
        for k,v in es_item.iteritems():
            if v and k != 'id':
                try:
                    mongo_result.__setitem__(k, v)
                except:
                    pass

        mongo_result.name = es_item['mainEntityOfPage_raw']
        mongo_result.site = self.url2domain(mongo_result.source)
        mongo_result.confidence = str(mongo_result.confidence)


        return mongo_result

    def get_nid(self, name):
        ret_list = Hentity.objects(alias__in=[u'\u5c71\u8331\u8438'])
        max_length = -1
        longest_ret = None
        for ret in ret_list:
            if len(ret['alias']) > max_length:
                max_length = len(ret['alias'])
                longest_ret = ret
        self.nids[name] = longest_ret['nid']
        return longest_ret['nid']
if __name__ == '__main__':
    m = YtyaocaiCleansing('ytyaocai-20160815')
    m.run()
                         