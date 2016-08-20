#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from mongoengine import *
from hcrawler_models import Hprice, Hentity
from hprice_cleaning import HpriceCleansing

import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

DB = 'hcrawler'
connect(db = DB, host='localhost:27017', username = 'hcrawler', password = 'f#d1p9c')

class YtyaocaiCleansing(HpriceCleansing):
    def parse_single_item(self, item):
        for k,v in item[u'price_history'].iteritems():
            mongo_item = Hprice()
            mongo_item.productPlaceOfOrigin = item[u'info'][u'产地']
            mongo_item.unitText = u'元/千克'
            mongo_item.confidence = '0.7'
            mongo_item.name = item['name']
            mongo_item.productGrade = item[u'info'][u'规格']
            #product的命名逻辑：如果数据没有等级字段，那么productgrade代表规格;如果有等级字段，那么productgrade代表等级，specific代表规格!
    
            name = mongo_item.name 
            mongo_item.mainEntityOfPage = self.nameMapper.get(name, name)
            mongo_item.nid = self.nids.get(name, self.get_nid(name))#从数据库得到nid，放在循环外并利用缓存以减少查询速度
            mongo_item.validDate = k   #日期
            mongo_item.price     = v   #价格
            mongo_item.site = self.url2domain(item[u'source'])

            properties = {
                    u"十二个月盈利比例" : item[u'info'][u"十二个月盈利比例"] ,
                    u"市净率" : item[u'info'][u"市净率"] ,
                    u"生产市值" : item[u'info'][u"生产市值"],
                    u"代码" : item[u'info'][u"代码"],
                    u"九个月盈利比例" : item[u'info'][u"九个月盈利比例"] ,
                    u"生长周期" : item[u'info'][u"生长周期"] ,
                    u"浮动市值" : item[u'info'][u"浮动市值"] ,
                    u"关注度" : item[u'info'][u"关注度"] ,
                    u"三个月盈利比例" : item[u'info'][u"三个月盈利比例"] ,
                    u"权重比" : item[u'info'][u"权重比"] ,
                    u"生长环境" : item[u'info'][u"生长环境"] ,
                    u"六个月盈利比例" : item[u'info'][u"六个月盈利比例"] ,
            }
            mongo_item.properties = properties
            self.counter +=1
            if not self.counter%100:
                print self.counter
            mongo_item.save()

    def get_nid(self, name):
        ret_list = Hentity.objects(alias__in = [name])
        if not ret_list:
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
    m = YtyaocaiCleansing('ytyaocai-20160815')
    m.run()
                         