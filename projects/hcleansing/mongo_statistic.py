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

def slack(msg):
    data={
        "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))


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

    def insert_log(self):
        print ('price statistics')

        log_record = {                                          # 因为counter的key格式是 www.100ppi.com 带.符号，不可直接作为mongo的key，所以先选择直接dumps，结构有待改进
            'log_record_date'        :  datetime.datetime.utcnow(),
            'price'              :  json.dumps(self.price_counter, ensure_ascii=False),    
            'series'             :  json.dumps(self.series_counter, ensure_ascii=False),
            'product'            :  json.dumps(self.product_counter, ensure_ascii=False),
            'total_price_record' :  self.total_price_record,
        }
        self.log.insert(log_record)

    def get_records_by_date(self, start, end):  # 需传入isodate格式 ,输出：时间区间内最新和最旧的两条record
        cursor =  self.log.find({
            'log_record_date':{
                '$gte': start,
                '$lt': end
        }})
        records = []
        for record in cursor:
            records.append(record)
        records.sort(key = lambda ele:ele[u'log_record_date'], reverse=0)
        oldest_record = records[0]
        newest_record = records[-1]
        return oldest_record, newest_record

    def compare_two_records(self, base_record, head_record):
        delta_record = {}
        for key, value in base_record.iteritems():  # key示例：u'product', u'total_price_record', u'series', u'price', u'log_record_date', u'_id'
            if isinstance(value, unicode):
                base_item = json.loads(value)
                head_item = json.loads(head_record[key])
                delta_record[key] = {}
                for domain in base_item.keys():
                    delta_record[key][domain] =  head_item[domain] -  base_item[domain]
            elif isinstance(value, int):  # 此时key为 total_price_record
                delta_record[key]   = head_record[key] -  base_record[key]

        slack('mongoDB record daily statistic:{}'.format(json.dumps(delta_record)))

    def daily_statistic(self, days_delta=1):
        now = datetime.datetime.utcnow()
        last = datetime.date.today() - datetime.timedelta(days=days_delta)  # 使用today是为了为了取到N天前的0点，而不是往前走24*N小时
        last = datetime.datetime(*(last.timetuple()[:6]))
        oldest_record, newest_record = self.get_records_by_date(last,now)
        self.compare_two_records(oldest_record, newest_record)

    def run(self):
        self.get_statistics()
        self.insert_log()
        self.daily_statistic()

if __name__ == '__main__':
    obj = mongoStatistic()
    obj.run()
