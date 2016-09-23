#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

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

class KmzyLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):

        domain = self.url2domain(jsn[u'source'])
        name = jsn[u'name'].encode('utf-8')
        specs = jsn[u'specs'].encode('utf-8')
        productGrade = specs.split('/')[0]
        productPlaceOfOrigin = specs.split('/')[1]
        sellerMarket = ''
        priceType = ''
        print(name)
        for validDate, price in jsn[u'data']:
            trackingId = hashlib.sha1('{}_{}'.format(jsn[u'source'], jsn[u'access_time'])).hexdigest()
            
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
                    'url': jsn[u'source'],
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
            record['claims'].append({'p': u'规格', 'o': productGrade})
            record['claims'].append({'p': u'币种', 'o': u'CNY' })
            record['recordDate'] = datetime.strptime('{}-01'.format(validDate), '%Y-%m-%d')
            try:
                self.node.insert(record)
            except DuplicateKeyError as e:
                print (e)
            
        # print(json.dumps(record, ensure_ascii=False, indent=4).encode('utf-8'))
        
if __name__ == '__main__':
    obj = KmzyLoader()
    obj.read_jsn('/data/hproject/2016/kmzy-20160905')