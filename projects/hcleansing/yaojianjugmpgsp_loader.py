#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

# from __future__ import print_function, division

import json
import os
import hashlib
import re
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from loader import Loader
from hzlib import libfile
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class YaojianjugmpgspLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        published_time = jsn['published_time']
        published_time = re.sub(u'发布', '', published_time).strip()
        time_array = time.strptime(published_time, u'%Y年%m月%d日')
        published_time = time.strftime(u'%Y-%m-%d', time_array)  # 年月日转化为-形式
        jsn['published_time'] = published_time
        for table in jsn[u'table_list']:
            source = jsn[u'source']
            domain = Loader.url2domain(source)
            trackingId = hashlib.sha1('{}_{}'.format(source, table[u'access_time'])).hexdigest()
            rid = hashlib.sha1('{}_{}_{}'.format(jsn[u'title'], table[u'access_time'], domain)).hexdigest()
            gid = rid
            tags = []
            if u'CL03' in source:       # 根据url进行分类
                tags.append('GSP')
            else:
                tags.append('GMP')
            record = {
                    'gid': gid,
                    'rid': rid,
                    'tags': tags,
                    'claims': [],
                    'recordDate': jsn['published_time'],
                    'createdTime': datetime.utcnow(),
                    'updatedTime': datetime.utcnow(),
                    'source': {
                        'url': source,
                        'domain': domain,
                        'trackingId': trackingId,
                        'confidence': '0.9', 
                    },
            }
            record['claims'].append({ 'p': '标题', 'o': jsn[u'title'] })
            record['claims'].append({ 'p': '发布时间', 'o': jsn[u'published_time']})
            record['claims'].append({ 'p': '正文', 'o': jsn[u'article_content']})
            del table[u'access_time']
            for key in table:
                record['claims'].append({ 'p': key, 'o': table[key]})
            try:
                self.records.insert(record)
            except DuplicateKeyError as e:
                print(e)

if __name__ == '__main__':
    obj = YaojianjugmpgspLoader()
    obj.read_jsn('/data/hproject/2016/')


