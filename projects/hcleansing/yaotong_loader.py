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

class YaotongLoader(Loader):

    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)


    def parse(self, jsn):
        domain = self.url2domain(jsn[u'source'])
        name = jsn[u'name'].encode('utf-8')
        for validDate, price in jsn[u'price_history'].iteritems():
            trackingId = hashlib.sha1('{}_{}'.format(jsn[u'source'], jsn[u'access_time'])).hexdigest()
            priceType = ''  # 药通的价格类型为空
            tags = [name, priceType, jsn[u'productPlaceOfOrigin'], jsn[u'sellerMarket'], jsn['productGrade']]
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
                    'confidence': '0.7', 
                },
                'claims': [],
            }

            record['claims'].append({'p': u'productName', 'o': name})
            record['claims'].append({'p': u'validDate', 'o': validDate})
            record['claims'].append({'p': u'价格', 'o': price})
            record['claims'].append({'p': u'unitText', 'o': u'元/千克',})
            record['claims'].append({'p': u'productPlaceOfOrigin','o': jsn[u'productPlaceOfOrigin']})
            record['claims'].append({'p': u'sellerMarket', 'o': jsn[u'sellerMarket']})
            record['claims'].append({'p': u'productGrade', 'o': jsn[u'productGrade']})
            record['claims'].append({'p': u'priceCurrency', 'o': u'CNY' })
            record['quotedTime'] = datetime.strptime(validDate, '%Y-%m-%d')
            try:
                self.node.insert(record)
            except DuplicateKeyError as e:
                print (e)
        print (name)    
            
        # print(json.dumps(record, ensure_ascii=False, indent=4).encode('utf-8'))
        
if __name__ == '__main__':
    obj = YaotongLoader()
    obj.read_jsn('/data/hproject/2016/yaotongnew-20160904')