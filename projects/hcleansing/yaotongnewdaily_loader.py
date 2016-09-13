#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# 总数据接近5000条，插入时会有10条左右的record重复


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


class YaotongnewdailyLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        source = 'http://www.yt1998.com/priceInfo.html'
        domain = self.url2domain(source)
        for row in jsn[u'data']:
            trackingId = hashlib.sha1('{}_{}'.format(source, row[u'access_time'])).hexdigest()
            name = row[u'ycnam']
            priceType = ''
            productPlaceOfOrigin = row[u'chandi']
            sellerMarket = row[u'shichang'] + u'市场'
            productGrade = row[u'guige']
            validDate = row[u'dtm']
            price = row[u'pri']
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
                    'confidence': '0.7', 
                },
                'claims': [],
            }
            record['claims'].append({'p': u'productName', 'o': name})
            record['claims'].append({'p': u'validDate', 'o': validDate})
            record['claims'].append({'p': u'价格', 'o': str(price)})
            record['claims'].append({'p': u'unitText', 'o': u'元/千克',})
            record['claims'].append({'p': u'productPlaceOfOrigin','o': productPlaceOfOrigin})
            record['claims'].append({'p': u'sellerMarket','o': sellerMarket})
            record['claims'].append({'p': u'productGrade', 'o': productGrade})
            record['claims'].append({'p': u'priceCurrency', 'o': u'CNY' })
            record['quotedTime'] = datetime.strptime(validDate, '%Y-%m-%d')
            try:
                self.node.insert(record)
            except DuplicateKeyError as e:
                print (e)


if __name__ == '__main__':
    obj = YaotongnewdailyLoader()
    obj.read_jsn('/tmp/yaotongnewdaily-20160913')