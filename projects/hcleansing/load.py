#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import os
import hashlib

from urlparse import urlparse
from hzlib import libfile

def connect():
    from pymongo import MongoClient
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client['kgbrain']
    return db['entity']
    # db['node']

def url2domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    domain = re.sub("^.+@","",domain)
    domain = re.sub(":.+$","",domain)
    return domain

def read_file():
    data_dir = '/tmp/zysj-20160830'
    for fname in os.listdir(data_dir):
        for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
            zysj_parse(js)
            break
        break

def zysj_parse(jsn):
    print(json.dumps(jsn, ensure_ascii=False, indent=4))
    for name, value in jsn.iteritems():
        for book, data in value.iteritems():
            domain = url2domain(data[u'source'])
            nid = hashlib.sha1('{}_{}'.format(name, domain))
            gid = nid
            trackingId = hashlib.sha1('{}_{}'.format(data[u'source'], ))
            print(name, book)


read_file()
