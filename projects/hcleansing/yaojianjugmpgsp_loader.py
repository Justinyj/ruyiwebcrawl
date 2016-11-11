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

from collections import Counter

class YaojianjugmpgspLoader(Loader):
    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def get_tag_from_content(self, word):
        rule_list = [
            [u'违反了(.*)收回', u'撤销'],
            [u'符合(.*)要求', u'发布'],
            [u'申请变更(.*)公示', u'发布'],
            [u'依法补发', u'发布'],
            [u'符合(.*)发给', u'发布']
        ]
        for rule_tuple in rule_list:
            rule_string = rule_tuple[0]
            if re.search(rule_string, word):
                return rule_tuple[1]
        return


    def get_tag_from_title(self, word):
        rule_list = [
            [u'撤销', u'撤销'],
            [u'认证公告|认证公示', u'发布'],
            [u'认证审查公告',  u'发布'],
            [u'发回', u'发回'],
            [u'收回', u'撤销'],
            [u'认证(.*)公示', u'发布'],
            [u'延续' , u'发布'],
            [u'注销', u'撤销'],
            [u'核发', u'发布'],
            [u'国家食品药品监督管理总局关于浙江尖峰药业有限公司药品GMP公告', u'发布']
        ]        
        for rule_tuple in rule_list:
            rule_string = rule_tuple[0]
            if re.search(rule_string, word):
                return rule_tuple[1]
        return 

    def parse(self, jsn):
        published_time = jsn['published_time']
        published_time = re.sub(u'发布', '', published_time).strip()
        try:
            time_array = time.strptime(published_time, u'%Y年%m月%d日')
        except:
            with open('luanma.txt','a') as f:
                f.write(jsn[u'source'] + '\n')
            return
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

            type_tag = self.get_tag_from_title(jsn[u'title'])
            if not type_tag:
                type_tag = self.get_tag_from_content(jsn[u'article_content'])
            if type_tag:
                tags.append(type_tag)
            else:
                with open('type_failed.txt','a') as f:
                    f.write(source + '\n')              
                return

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
                if len(key) > 30 or u'有限公司' in key:
                    with open('wrong_url.txt','a') as f:
                        f.write(source + '\n')
                    return

            for key in table:
                if u'证书编号' in key or u'企业名称' in key:
                    break
            else:
                with open('wrong_url.txt','a') as f:
                    f.write(source + '\n')
                return

            for key in table:
                new_key = re.sub(u'[\s   　]', u'',key.strip())  # \s  之后是一种不同的空格！
                if not self.tag_counter.get(new_key, None):
                    self.tag_counter[new_key] = {
                        'counts':0,
                        'eg'    :source,
                    }
                self.tag_counter[new_key]['counts'] += 1
                record['claims'].append({ 'p': key, 'o': table[key]})

            try:
                continue
                self.records.insert(record)
            except DuplicateKeyError as e:
                print(e)

if __name__ == '__main__':
    obj = YaojianjugmpgspLoader()
    obj.tag_counter = {}
    obj.read_jsn('/data/hproject/2016/yaojianjugmpgsp-1109/')
    print json.dumps(obj.tag_counter, ensure_ascii=False)


