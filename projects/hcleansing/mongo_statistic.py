# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from pymongo import MongoClient
from collections import Counter

import json
import datetime
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class mongoStatistic(object):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.entity = db['entities']
        self.node = db['price']  # 无论mongo服务器开启关闭，以上语句都可成功执行
        self.meta = db['pricemeta']
        self.log  = db['log']

        self.series_counter    = Counter()
        self.product_counter   = Counter()
        self.price_counter = Counter() 
        self.total_price_record = 0
        self.domain_list =[
            'www.kmzyw.com.cn',
            'www.yt1998.com',
            'www.100ppi.com',
            'www.zyctd.com',
        ]
    
    def get_statistics(self):
        # TODO 更改成使用查询条件查询，增加查询速度

        for domain in self.domain_list:
            record_num = self.node.count({'source.domain':domain})
            self.total_price_record += record_num
            self.price_counter[domain] = record_num

            series_num = len(self.node.distinct('series', {'source.domain':domain}))
            self.series_counter[domain] = series_num

            product_num = len(self.node.distinct('tags.0', {'source.domain':domain})) # tags的第一个标签是种类
            self.product_counter[domain] = product_num
        return

    def output_counter(self):
        print ('price statistics')

        log_record = {                                          # 因为counter的key格式是 www.100ppi.com 带.符号，不可直接作为mongo的key，所以先选择直接dumps，结构有待改进
            'log_record_date'        :  datetime.datetime.utcnow(),
            'price'              :  json.dumps(self.price_counter, ensure_ascii=False),    
            'series'             :  json.dumps(self.series_counter, ensure_ascii=False),
            'product'            :  json.dumps(self.product_counter, ensure_ascii=False),
            'total_price_record' :  self.total_price_record,
        }
        self.log.insert(log_record)

    def run(self):
        self.get_statistics()
        self.output_counter()

if __name__ == '__main__':
    obj = mongoStatistic()
    obj.run()
