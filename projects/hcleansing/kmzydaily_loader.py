#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# 数据说明：（总数据条数为271*20=5420条左右）
# 1.有5%左右的数据是重复的，即完全一样，经检验是网站方面的问题，导入时会有三百条报重复，属正常情况。
# 2.9月12号时，对数据中validDate分布的统计：  Counter({u'2016-09-11': 3708, u'2016-09-09': 909, u'2016-08-20': 792, u'2016-08-28': 2, u'2016-08-25': 1, u'2016-09-05': 1})


from __future__ import print_function, division

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


class KmzydailyLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        source = jsn[u'source']
        domain = self.url2domain(source)

        for row in jsn[u'rows']:
            trackingId = hashlib.sha1('{}_{}'.format(source, row[u'access_time'])).hexdigest()
            name = row[u'drug_name']
            priceType = ''
            productPlaceOfOrigin = row[u'origin']
            sellerMarket = row[u'site']
            productGrade = row[u'standards']
            validDate = row[u'price_date']
            price = row[u'price']

            tags = [name, priceType, productPlaceOfOrigin, sellerMarket, productGrade]
            rid = hashlib.sha1('{}_{}_{}'.format('_'.join(tags), validDate, domain)).hexdigest()

            record = {
                'rid': rid,
                'gid': rid, # 不可变
                'series': '_'.join(tags),
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
            except DuplicateKeyError as e:
                print (e)


if __name__ == '__main__':
    obj = KmzydailyLoader()
    obj.read_jsn('/data/hproject/2016/kmzydaily-20160912')
