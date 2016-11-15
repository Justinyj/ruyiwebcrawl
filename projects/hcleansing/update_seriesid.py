#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>


import json
import re
import requests
import os


from urlparse import urlparse
from pymongo import MongoClient
from datetime import datetime



def main():
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client['kgbrain']
    node = db['news']
    meta = db['pricemetatest']
    meta.create_index('series', unique=True)
    for i in node.find():
        # series = i['series']
        # domain = i['source']['domain']
        # seriesid = u'{}_{}'.format(series, domain)
        # print help(i)
        print i['test']
        node.update({'source.domain':'www.yt1998.com'},{"$set":{"test":'source.domain123'}},False, True)
        break

if __name__ == '__main__':
    main()