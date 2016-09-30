#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

# from __future__ import print_function, division

import json
import os
import hashlib
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from loader import Loader
from hzlib import libfile
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ZhongyaocaitdLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                try:
                    self.parse(js)
                except Exception, e:
                    print ('{}: {}'.format(type(e), e.message))

    def parse(self, jsn):
        self.success = 0
        source = jsn[u'source']
        domain = self.url2domain(source)
        name = jsn[u'name']
        priceType = ''
        productPlaceOfOrigin = jsn[u'productPlaceOfOrigin']
        productGrade         = jsn[u'productGrade']
        price_item_list      = jsn[u'price_data']
        series_cache = set()
        print name
        for row in price_item_list:                         # 格式 {"sellerMarket": "玉林药市", "price": 57.0, "validDate": "2016-09-26", "access_time": "2016-09-30T04:42:25.371477"}
            trackingId = hashlib.sha1('{}_{}'.format(source, row[u'access_time'])).hexdigest()
            sellerMarket = row[u'sellerMarket'].replace(u'药市', u'市场')
            validDate = row[u'validDate']
            price = row[u'price']
            tags = [name, priceType, productPlaceOfOrigin, sellerMarket, productGrade]
            rid = hashlib.sha1('{}_{}_{}'.format('_'.join(tags), validDate, domain)).hexdigest()
            series = '_'.join(tags)
            if series not in series_cache:
                self.insert_meta_by_series(series)
                series_cache.add(series)
            record = {
                'rid': rid,
                'gid': rid, # 不可变
                'series': series,
                'tags': [ tag for tag in tags if tag],
                'createdTime': datetime.utcnow(),
                'updatedTime': datetime.utcnow(),
                'source': {
                    'url': source,
                    'domain': domain,
                    'trackingId': trackingId,
                    'confidence': '0.6', 
                },
                'claims': [],
            }
            record['claims'].append({'p': u'商品名称', 'o': name})
            record['claims'].append({'p': u'日期', 'o': validDate})
            record['claims'].append({'p': u'价格', 'o': str(price)})
            record['claims'].append({'p': u'价格单位', 'o': u'元/千克',})
            record['claims'].append({'p': u'产地','o': productPlaceOfOrigin})
            record['claims'].append({'p': u'报价地点','o': sellerMarket})
            record['claims'].append({'p': u'规格', 'o': productGrade})
            record['claims'].append({'p': u'币种', 'o': u'CNY' })
            record['recordDate'] = validDate
            try:
                self.node.insert(record)
                self.success += 1
            except DuplicateKeyError as e:
                print (e)
        print ('success: {}'.format(self.success))



if __name__ == '__main__':
    obj = ZhongyaocaitdLoader()
    obj.read_jsn('/data/hproject/2016/zhongyaocaitd-20160930')