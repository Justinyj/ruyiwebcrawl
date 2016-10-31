#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

# from __future__ import print_function, division

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


class ZhongyaocaitdnewsLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        for news_item in jsn:           # 每个jsn代表一页，其中有10条新闻
            source = news_item[u'news_url']
            domain = Loader.url2domain(source)
            trackingId = hashlib.sha1('{}_{}'.format(source, news_item[u'access_time'])).hexdigest()
            rid = hashlib.sha1('{}_{}_{}'.format(news_item[u'news_title'], news_item[u'news_date'], domain)).hexdigest()
            gid = rid
            tags = [u'新闻']
            tags.extend(news_item[u'news_keyword_list'])
            tags.append(news_item[u'news_type'])            # 市场快讯等
            record = {
                    'gid': gid,
                    'rid': rid,
                    'tags': tags,
                    'claims': [],
                    'createdTime': datetime.utcnow(),
                    'updatedTime': datetime.utcnow(),
                    'source': {
                        'url': source,
                        'domain': domain,
                        'trackingId': trackingId,
                        'confidence': '0.7', 
                    },
            }
            record['claims'].append({ 'p': '标题', 'o': news_item[u'news_title'] })
            record['claims'].append({ 'p': '摘要', 'o': news_item[u'news_desc'] })
            record['claims'].append({ 'p': '来源', 'o': u'中药材天地网'})
            record['claims'].append({ 'p': '日期', 'o': news_item[u'news_date'][:10] })
            record['claims'].append({ 'p': '链接', 'o': source })
            record['claims'].append({ 'p': '正文', 'o': news_item[u'news_content'] })
            # print record
            try:
                self.news.insert(record)
            except DuplicateKeyError as e:
                print(e)
            # print json.dumps(record, ensure_ascii=False)
if __name__ == '__main__':
    obj = ZhongyaocaitdnewsLoader()
    obj.read_jsn('/Users/johnson/google')