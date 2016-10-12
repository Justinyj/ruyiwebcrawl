# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>


from pymongo import MongoClient
from collections import Counter

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
        self.series_counter    = {}
        self.product_counter   = {}
        self.price_counter = Counter() 
    
    def run(self):
        # TODO 更改成使用查询条件查询，增加查询速度
        cursor = self.node.find()
        for record in cursor:
            domain = record[u'source'][u'domain']

            self.price_counter[domain] += 1                           # 统计价格条数
            if not self.series_counter.get(domain, None):
                self.series_counter[domain] = set()
            self.series_counter[domain].add(record[u'series'])  # 统计价格系列

            if not self.product_counter.get(domain, None):
                self.product_counter[domain] = set()

            self.product_counter[domain].add(record[u'tags'][0]) # 统计物料名

        self.output_counter()

    def output_counter(self):
        print ('price statistics')
        total = 0
        for k, v in self.price_counter.iteritems():
            total += v
            print '{} : {}'.format(k, v)
        print '{} : {}'.format('total', total)

        print ('\nseries statistics')
        total = set()
        for k, v in self.series_counter.iteritems():
            total.update(v)
            print '{} : {}'.format(k, len(v))
        print '{} : {}'.format('total', len(total))

        print ('\nproduct statistics')
        total = set()
        for k, v in self.product_counter.iteritems():
            total.update(v)
            print '{} : {}'.format(k, len(v))
        print '{} : {}'.format('total', len(total))

if __name__ == '__main__':
    obj = mongoStatistic()
    obj.run()
