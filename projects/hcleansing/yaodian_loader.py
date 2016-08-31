#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from __future__ import print_function, division

import json
import os
import hashlib
from datetime import datetime

from loader import Loader
from hzlib import libfile


class YaodianLoader(Loader):

    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.yaodian_parse(js)
                break
            break

    def yaodian_parse(self, jsn):
        name = jsn[u'name']
        domain = self.url2domain(jsn[u'source'])
        nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest() # apply sameAs映射后可变
        gid = nid # 不可变
        trackingId = hashlib.sha1('{}_{}'.format(jsn[u'source'], jsn[u'access_time'])).hexdigest()

        record = {
            'gid': gid,
            'nid': nid,
            'tags': [],
            'alias': [name],
            'claims': [],
            'createdTime': datetime.utcnow().isoformat(),
            'updatedTime': datetime.utcnow().isoformat(),
            'source': {
                'url': jsn[u'source'],
                'domain': domain,
                'trackingId': trackingId,
                'confidence': 0.9, 
            },
        }

        #claim

if __name__ == '__main__':
    obj = YaodianLoader()
    obj.read_jsn('/data/yaodian')