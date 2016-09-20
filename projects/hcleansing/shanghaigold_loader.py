#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>


from __future__ import print_function, division

import json
import os
import hashlib
import urllib
from datetime import datetime
import dateutil.parser
from loader import Loader
from hzlib import libfile
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ShanghaigoldLoader(Loader):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.collection = db['price']
        self.collection.create_index('gid', unique=True)
        

    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse_info(js)


    def parse_info(self, jsn):
        if u'合约' in jsn and 'Pt9995' in jsn[u'合约']:
            name = jsn[u'合约']
            validDate = jsn[u'日期']
            source = jsn[u'source']
            domain = self.url2domain(source)
            rid = hashlib.sha1('{}_{}_{}'.format(name, validDate, domain)).hexdigest()

            trackingId = hashlib.sha1('{}_{}'.format(source, jsn[u'access_time'])).hexdigest()

            record = {
                'gid': rid,
                'rid': rid,
                'tags': [name, u'铂金'],
                'series': '铂金_加权平均价__上海黄金交易所_',
                'claims': [],
                'createdTime': datetime.utcnow(),
                'updatedTime': datetime.utcnow(),
                'recordDate': validDate,
                'source': {
                    'url': source,
                    'domain': domain,
                    'trackingId': trackingId,
                    'confidence': 0.9, 
                },
            }
            record['claims'].append({'p': u'商品名称', 'o': name})
            if jsn[u'加权平均价'].strip():
                record['claims'].append({'p': u'价格', 'o': jsn[u'加权平均价']})
                record['claims'].append({'p': u'日期', 'o': validDate})
                record['claims'].append({'p': u'报价类型', 'o': u'加权平均价'})
                record['claims'].append({'p': u'价格单位', 'o': u'元/克'})
                print(jsn[u'加权平均价'])
                try:
                    self.collection.insert(record)
                except DuplicateKeyError as e:
                    print (e)
            

        
if __name__ == '__main__':
    obj = ShanghaigoldLoader()
    obj.read_jsn('/data/hproject/2016/shanghaigold-20160918')
