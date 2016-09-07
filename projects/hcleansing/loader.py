#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import re

from urlparse import urlparse
from pymongo import MongoClient


class Loader(object):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.entity = db['entities']
        self.entity.create_index('nid', unique=True)
        self.node = db['price']
        self.node.create_index('rid', unique=True)

    @staticmethod
    def url2domain(url):
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        domain = re.sub("^.+@","",domain)
        domain = re.sub(":.+$","",domain)
        return domain

    def read_jsn(self, data_dir):
        pass

    def parser(self, jsn):
        pass

    @staticmethod
    def get_tags_alias(tags_datadir):
        """ 只有把名字对应到实体，才有tags和alias两个字段可以加入
        """
        tags_dict = {}
        alias_dict = {}
        for f in os.listdir(tags_datadir):
            fname = os.path.join(tags_datadir, f)
            with open(fname) as fd:
                for entity, dic in json.load(fd).iteritems():

                    for label, value in dic.iteritems():
                        if label == u'Tags':
                            tags_dict[entity] = value
                        elif label == u'av pair':
                            for a, v in value:
                                if a in [u'别名',u'又称',u'其他名称']:
                                    if entity not in alias_dict:
                                        alias_dict[entity] = [v]
                                    else:
                                        alias_dict[entity].append(v)
        return tags_dict, alias_dict
