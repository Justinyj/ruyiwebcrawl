#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

# from __future__ import print_function, division

import json
import os
import hashlib
import re
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from loader import Loader
from hzlib import libfile
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class YaotongwangnewsLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        for news_item in jsn:           # 每个jsn代表一页，其中有10条新闻
            source = news_item[u'news_url']
            domain = Loader.url2domain(source)
            trackingId = hashlib.sha1('{}_{}'.format(source, news_item[u'access_time'])).hexdigest()
            rid = hashlib.sha1('{}_{}_{}'.format(news_item[u'news_title'], news_item[u'news_date'], domain)).hexdigest()    # 这里news_data是一个拼写错误，下批爬取会改回来
            gid = rid
            tags = [u'新闻']
            dealed_keyword_list = re.split(u' |、', news_item[u'news_keyword_list'][0])  # 药通网的news_keyword_list 为长度仅为1的列表
            tags.extend(dealed_keyword_list)
            tags.append(news_item[u'news_type'])            # 市场快讯等
            if news_item[u'market']:                        # 部分新闻会含市场信息
                tags.append(news_item[u'market'])
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
            record['claims'].append({ 'p': '来源', 'o': u'药通网'})
            record['claims'].append({ 'p': '日期', 'o': news_item[u'news_date'][:10] })
            record['claims'].append({ 'p': '链接', 'o': source })
            record['claims'].append({ 'p': '正文', 'o': news_item[u'news_content'] })
            try:
                self.news.insert(record)
            except DuplicateKeyError as e:
                print(e)

if __name__ == '__main__':
    obj = YaotongwangnewsLoader()
    obj.read_jsn('/data/hproject/2016/yaotongwangnews-1031')