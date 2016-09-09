#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>


from __future__ import print_function, division

import json
import os
import hashlib
import urllib
from datetime import datetime

from loader import Loader
from hzlib import libfile
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class QichachaLoader(Loader):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.biz = db['enterprises']
        self.biz.create_index('gid', unique=True)
        self.ridstart = 0
        self.url_pattern = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab=base"


    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse_info(js)
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse_subcompany(js)


    def parse_info(self, jsn):
        self.ridstart = 0
        
        def generate_rid():
            self.ridstart += 1
            return '_' + str(self.ridstart * 11)

        if u'info' in jsn:
            name = jsn[u'name']
            source = jsn[u'source'].replace(name, urllib.quote(str(name)))
            domain = self.url2domain(source)
            nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest() # apply sameAs映射后可变
            gid = nid # 不可变
            trackingId = hashlib.sha1('{}_{}'.format(source, jsn[u'access_time'])).hexdigest()

            record = {
                'gid': gid,
                'nid': nid,
                'alias': [name],
                'claims': [],
                'createdTime': datetime.utcnow(),
                'updatedTime': datetime.utcnow(),
                'source': {
                    'url': source,
                    'domain': domain,
                    'trackingId': trackingId,
                    'confidence': 0.9, 
                },
            }

            for item in jsn[u'info']:
                if item[1] is not None:
                    record['claims'].append({'p': item[0], 'o': item[1]})

            for holder in jsn[u'shareholders']:
                rid = generate_rid()
                record['claims'].append({'p': u'股东信息', 'rid': rid})
                record['claims'].append({'p': u'股东名称', 'o': holder[u'name'], 'rid': rid})
                record['claims'].append({'p': u'股东职务', 'o': holder[u'role'], 'rid': rid})
                if holder[u'link'] is not None:
                    key_num = holder[u'link'].split('_')[1]
                    record['claims'].append({'p': u'股东source_url', 'o': self.url_pattern.format(key_num=key_num, name=urllib.quote(str(holder[u'name']))), 'rid': rid})

            for change in jsn[u'changes']:
                rid = generate_rid()
                record['claims'].append({'p': u'变更记录', 'rid': rid})
                record['claims'].append({'p': u'变更项目', 'o': change[u'project'], 'rid': rid})
                record['claims'].append({'p': u'变更时间', 'o': change[u'change_time'], 'rid': rid})
                record['claims'].append({'p': u'变更前', 'o': change[u'before_change'], 'rid': rid})
                record['claims'].append({'p': u'变更后', 'o': change[u'after_change'], 'rid': rid})

            for executive in jsn[u'executives']:
                rid = generate_rid()
                record['claims'].append({'p': u'主要人员', 'rid': rid})
                record['claims'].append({'p': u'人员职务', 'o': executive[u'position'], 'rid': rid})
                record['claims'].append({'p': u'人员姓名', 'o': executive[u'name'], 'rid': rid})



            try:
                self.biz.insert(record)
            except DuplicateKeyError as e:
                print(e)
            # del record['_id']
            # print(json.dumps(record, encoding='utf-8', ensure_ascii=False, indent=4))

    def parse_subcompany(self, jsn):
        self.ridstart = 0
        def generate_rid():
            self.ridstart += 1
            return '_' + str(self.ridstart * 111)
        if u'sub_companies' in jsn:
            name = jsn[u'name']
            source = jsn[u'source'].replace(name, urllib.quote(str(name)))
            domain = self.url2domain(source)
            nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest()
            entity = self.biz.find_one({'nid': nid})
            if not entity:
                return
            claims = entity['claims']

            for subcomp in jsn[u'sub_companies']:
                rid = generate_rid()
                key_num = subcomp[u'key_num']
                claims.append({'p': u'对外投资', 'rid': rid})
                claims.append({'p': u'子公司名称', 'o': subcomp[u'name'], 'rid': rid})
                claims.append({'p': u'source.url', 'o': self.url_pattern.format(key_num=key_num, name=urllib.quote(str(subcomp[u'name']))), 'rid': rid })
            
            updated = self.biz.update_one({'nid': nid}, { '$set': { 'claims': claims}})
            # print(json.dumps(entity['claims'], ensure_ascii=False))

        
if __name__ == '__main__':
    obj = QichachaLoader()
    obj.read_jsn('/data/hproject/2016/qichacha-20160902')
