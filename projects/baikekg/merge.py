#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import urllib
import json
import os
import time
from collections import defaultdict, Counter

def merge_fudankg(bucketname):
    """ TODO need generate url from entities file.
        or the old style url will cause lack of tags and info.
    """
    batch_id = 'fudankg-json-20160625'
    saved_dir = 'fudankg_saved'
    data = defaultdict(dict)
    entities = set()
    gcounter = Counter()
    start_time = time.time()

    def find_other_package(entity, original):
        if original not in [u'av path', u'Information', u'Tags']:
            return

        ent = urllib.quote(entity.encode('utf-8'))
        urlpattern = {
            u'av pair': 'https://crl.ptopenlab.com:8800/cndbpedia/api/entityAVP?entity={}',
            u'Information': 'https://crl.ptopenlab.com:8800/cndbpedia/api/entityInformation?entity={}',
            u'Tags': 'https://crl.ptopenlab.com:8800/cndbpedia/api/entityTag?entity={}',
        }

        for k, v in urlpattern.iteritems():
            gcounter[k] += 1
            if k == original:
                continue

            url = v.format(ent)
            url_hash = hashlib.sha1(url).hexdigest()
            filename = '{}_{}'.format(batch_id, url_hash)
            fname = os.path.join(bucketname, filename[-1], filename)
            if not os.path.exists(fname):
                continue
            with open(fname) as fd:
                js = json.load(fd)
            _, v = js.items()[0]
            data[entity][k] = v[k]


    for fdir in os.listdir(bucketname):
        fdir = os.path.join(bucketname, fdir)
        for f in os.listdir(fdir):
            fname = os.path.join(fdir, f)
            with open(fname) as fd:
                js = json.loads(fd.read())
            for entity, v in js.items():
                if entity in entities:
                    continue

            if u'Tags' in v:
                if v[u'Tags'] != []:
                    data[entity][u'Tags'] = v[u'Tags']
                find_other_package(entity, u'Tags')
                entities.add(entity)
            elif u'Information' in v:
                if v[u'Information'] != u'' and v[u'Information'] != []:
                    data[entity][u'Information'] = v[u'Information']
                find_other_package(entity, u'Information')
                entities.add(entity)
            elif u'av pair' in v:
                if v[u'av pair'] != []:
                    data[entity][u'av pair'] = v[u'av pair']
                find_other_package(entity, u'av pair')
                entities.add(entity)

            gcounter['count'] += 1
            if len(data) > 10000:
                saved_filename = os.path.join(saved_dir, str(gcounter['count']))
                print('10 thousand entities passed, {} /s'.format(gcounter['count'] / (time.time() - start_time)))
                with open(saved_filename, 'w') as fd:
                    json.dump(data, fd)
                data = defaultdict(dict)

    if len(data) >= 1:
        saved_filename = os.path.join(saved_dir, str(gcounter['count']))
        with open(saved_filename, 'w') as fd:
            json.dump(data, fd)

    print(gcounter)


if __name__ == '__main__':
    merge_fudankg('fudankg-json')
