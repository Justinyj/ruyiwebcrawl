#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import os
import hashlib
from datetime import datetime

from loader import Loader
from hzlib import libfile

class ZysjLoader(Loader):

    def read_jsn(self, data_dir):
        data_dir = '/tmp/zysj-20160831'
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                zysj_parse(js)
                break
            break

    def parse(self, jsn):
        print(json.dumps(jsn, ensure_ascii=False, indent=4))
        for name, value in jsn.iteritems():
            for book, data in value.iteritems():
                domain = url2domain(data[u'source'])
                nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest() # apply sameAs映射后可变
                gid = nid # 不可变
                trackingId = hashlib.sha1('{}_{}'.format(data[u'source'], data[u'access_time'])).hexdigest()

                record = {
                    'gid': gid,
                    'nid': nid,
                    'tags': [],
                    'alias': [name],
                    'claims': [],
                    'createdTime': datetime.utcnow().isoformat(),
                    'updatedTime': datetime.utcnow().isoformat(),
                    'source': {
                        'url': data[u'source'],
                        'domain': domain,
                        'trackingId': trackingId,
                        'confidence': 0.8,
                    },
                }
                for k, v in data.iteritems():
                    record['claims'].append( {'p': k, 'o': v} )
                print(record)

obj = ZysjLoader()
obj.read_jsn()

