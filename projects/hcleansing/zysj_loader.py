#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from datetime import datetime
from loader import Loader
from hzlib import libfile
import json
import os
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ZysjLoader(Loader):

    def read_jsn(self, data_dir):
        # data_dir = '/tmp/zysj-20160831'
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        # print(json.dumps(jsn, ensure_ascii=False, indent=4))
        books_data = jsn[u'books_data']
        domain = Loader.url2domain(jsn[u'source'])
        name = jsn[u'name']
        nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest() # apply sameAs映射后可变
        gid = nid # 不可变
        trackingId = hashlib.sha1('{}_{}'.format(jsn[u'source'], jsn[u'access_time'])).hexdigest()

        record = {
            'gid': gid,
            'nid': nid,
            # 'tags': [],
            'alias': [name],
            'claims': [],
            'createdTime': datetime.utcnow(),
            'updatedTime': datetime.utcnow(),
            'source': {
                'url': jsn[u'source'],
                'domain': domain,
                'trackingId': trackingId,
                'confidence': 0.8,
            },
        }

        for single_book in books_data:
            book_name = single_book.keys()[0]
            if book_name == u'《中药大辞典》':  # 有中药大辞典，优先选择
                chosen_book = single_book
                break
        else:                                # 遍历完不存在中药大辞典，则选择第一个 
            chosen_book = books_data[0]
        book_name = chosen_book.keys()[0]
        book_data = chosen_book[book_name]
        for item in book_data:
            for k, v in item.iteritems():
                if not v:
                    continue
                if k == u'来源': 
                    entity_definition = v
                    record['claims'].insert(0, {'p': u'实体定义', 'o': v}) # 实体定义加到最前面
                else:
                    record['claims'].append({'p': k, 'o': v})
                    
        for ele in record['claims']:
            k = ele.keys()[0]
            ele[k] = ele[k].strip()
        self.entity.insert(record)
        # print(json.dumps(record, ensure_ascii=False, indent=4).encode('utf-8'))

if __name__ == '__main__':
    obj = ZysjLoader()
    obj.read_jsn('/data/hproject/2016/zysj-20160902')
