#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from lib.libfile import readExcel

from datetime import timedelta, date, datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import hashlib
import json
import re


base = date(1900, 1, 1)
HEADER = [ '实体', 'o1', '日期', '标题', '摘要', '数据源', '数据更新时间', '原文链接' ]
FILE = '1111.xlsx'

# print file['Sheet1'][0:10]
class NewsLoader(object):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.header = None
        self.file = None
        self.news = db['news']
        self.news.create_index('gid', unique=True)

    def load_header(self, header):
        self.header = header

    def load_file(self, file):
        self.file = readExcel(self.header, file)


    @staticmethod
    def format_date(sheet):
        for item in sheet:
            # print item['日期']
            if item['日期'] != '':
                calculated = base + timedelta(days= int(item['日期']) - 2)
                item['日期'] = calculated.isoformat()
            if item['数据更新时间'] != '':
                calculated = base + timedelta(days= int(item['数据更新时间']) - 2)
                item['数据更新时间'] = calculated.isoformat()
        return sheet


    @staticmethod
    def url2domain(url):
        from urlparse import urlparse
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        domain = re.sub("^.+@","",domain)
        domain = re.sub(":.+$","",domain)
        return domain

    def save_to_db(self):
        for sh in self.file:
            sheet = self.file[sh]
            sheet = self.format_date(sheet)
            # print json.dumps(sheet[:3], ensure_ascii=False)


            for item in sheet:
                name = item['实体']
                tags = [ name, item['o1'], '新闻' ]
                source = item['原文链接']
                domain = self.url2domain(source)
                trackingId = hashlib.sha1('{}_{}'.format(source, datetime.utcnow().isoformat())).hexdigest()
                rid = hashlib.sha1('{}_{}_{}'.format(item['标题'], item['日期'], domain)).hexdigest()
                gid = rid
                if not source or not item['标题']:
                    continue
                record = {
                        'gid': gid,
                        'rid': rid,
                        'tags': tags,
                        'claims': [],
                        'createdTime': datetime.utcnow().isoformat(),
                        'updatedTime': datetime.utcnow().isoformat(),
                        'source': {
                            'url': source,
                            'domain': domain,
                            'trackingId': trackingId,
                            'confidence': "0.9", 
                        },
                }
                record['claims'].append({ 'p': '标题', 'o': item['标题'] })
                record['claims'].append({ 'p': '摘要', 'o': item['摘要'] })
                record['claims'].append({ 'p': '数据源', 'o': item['数据源'] })
                record['claims'].append({ 'p': '发布日期', 'o': item['日期'] })
                record['claims'].append({ 'p': '数据更新时间', 'o': item['数据更新时间']})
                print json.dumps(record, ensure_ascii=False)
                try:
                    self.news.insert(record)
                except DuplicateKeyError as e:
                    print(e)




        
if __name__ == '__main__':
    loader = NewsLoader()
    loader.load_header(HEADER)
    loader.load_file(FILE)
    loader.save_to_db()
    # ret = format_date(file['Sheet1'])

    # print json.dumps(ret[0:10], ensure_ascii=False)