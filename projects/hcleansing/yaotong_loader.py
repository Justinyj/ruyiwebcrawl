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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class YaodianLoader(Loader):

    def read_jsn(self, data_dir):
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)


    def parse(self, jsn):
        domain = self.url2domain(jsn[u'source'])
        name = jsn[u'name']
        nid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), domain)).hexdigest() # apply sameAs映射后可变
        gid = nid # 不可变
        for validDate, price in jsn[u'price_history'].iteritems():
            rid = hashlib.sha1('{}_{}'.format(name.encode('utf-8'), validDate)).hexdigest()
            trackingId = hashlib.sha1('{}_{}'.format(jsn[u'source'], jsn[u'access_time'])).hexdigest()
            tags = [name, jsn[u'sellerMarket'], jsn[u'productPlaceOfOrigin'], jsn['productGrade']]
            record = {
                'gid': gid,
                'rid': rid,
                'claims': [],
                'series': '-'.join(tags),
                'tags': tags,
                'createdTime': datetime.utcnow().isoformat(),  # 稍后记得删去 isof
                'updatedTime': datetime.utcnow().isoformat(),
                'deletedTime': '',
                'source': {
                    'url': jsn[u'source'],
                    'domain': domain,
                    'trackingId': trackingId,
                    'confidence': '0.7', 
                },
            }
            record['claims'].append({'p': u'商品', 'o': name, 'oNid': nid})
            record['claims'].append({'p': u'validDate', 'o': validDate})
            record['claims'].append({'p': u'price', 'o': price})
            record['claims'].append({'p': u'unitText', 'o': u'元/千克',})
            record['claims'].append({'p': u'sellerMarket', 'o': jsn[u'sellerMarket']})
            record['claims'].append({'p': u'productPlaceOfOrigin','o': jsn[u'productPlaceOfOrigin']})
            record['claims'].append({'p': u'productGrade', 'o': jsn[u'productGrade']})
            record['claims'].append({'p': u'priceCurrency', 'o': u'CNY' })
            # record['claims'].append({'p':,'o': })
            # record['claims'].append({'p':,'o': })
            # record['claims'].append({'p':,'o': })

            # break
    
    
            print(json.dumps(record, ensure_ascii=False, indent=4).encode('utf-8'))
        
if __name__ == '__main__':
    obj = YaodianLoader()
    # obj.read_jsn('/data/hproject/2016/yaotongnew-20160904')
    obj.read_jsn('/tmp/yaotongnew-20160904')