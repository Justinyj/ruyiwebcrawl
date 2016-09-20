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

class ChemppiLoader(Loader):
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
        name = jsn[u'name']
        validDate = jsn[u'发布时间']
        source = jsn[u'url']
        domain = self.url2domain(source)
        
        priceType = jsn[u'报价类型']
        productPlaceOfOrigin = jsn[u'出产地']
        sellerMarket = jsn[u'报价机构']
        productGrade = ''
        
        info = jsn[u'详细信息']
        for prop in info:
            if u'等级' in prop:
                productGrade = info[prop]
        
        tags = [name, priceType, productPlaceOfOrigin, sellerMarket, productGrade]
        rid = hashlib.sha1('{}_{}_{}'.format('_'.join(tags), validDate, domain)).hexdigest()
        trackingId = hashlib.sha1('{}_{}'.format(source, datetime.utcnow().isoformat())).hexdigest()
        price = ''.join([c for c in jsn[u'商品报价'] if c.isdigit() or c == '.'])
        unitText = ''.join([c for c in jsn[u'商品报价'] if not c.isdigit() and not c == '.'])
        record = {
            'gid': rid,
            'rid': rid,
            'tags': [tag for tag in tags if tag],
            'series': '_'.join(tags),
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
        
        record['claims'].append({'p': u'价格', 'o': price})
        record['claims'].append({'p': u'价格单位', 'o': unitText})
        record['claims'].append({'p': u'币种', 'o': u'CNY' })
        record['claims'].append({'p': u'日期', 'o': validDate})
        record['claims'].append({'p': u'报价类型', 'o': priceType})
        record['claims'].append({'p': u'报价机构', 'o': sellerMarket})
        
        if productPlaceOfOrigin:
            record['claims'].append({'p': u'出产地', 'o': productPlaceOfOrigin})
        if productGrade:
            record['claims'].append({'p': u'等级', 'o': productGrade})
        
        for k, v in info.iteritems():
            if v:
                record['claims'].append({'p': k, 'o': v})
        try:
            self.collection.insert(record)
        except DuplicateKeyError as e:
            print (e)
            

        
if __name__ == '__main__':
    obj = ChemppiLoader()
    obj.read_jsn('/data/hproject/2016/chemppi')
