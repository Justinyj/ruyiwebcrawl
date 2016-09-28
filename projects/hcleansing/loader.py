#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import re
import requests

from pymongo.errors import DuplicateKeyError
from urlparse import urlparse
from pymongo import MongoClient


def slack(msg):
    data={
        "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))


class Loader(object):
    def __init__(self):
        client = MongoClient('mongodb://127.0.0.1:27017')
        db = client['kgbrain']
        self.entity = db['entities']
        self.node = db['price']  # 无论mongo服务器开启关闭，以上语句都可成功执行
        self.meta = db['pricemeta']
        try:
            self.entity.create_index('gid', unique=True)
            self.node.create_index('gid', unique=True)
            self.node.create_index('series', unique=False)
            self.node.create_index('tags', unique=False)
            self.node.create_index('recordDate', unique=False)
            self.meta.create_index('attrs', unique=False)
            self.meta.create_index('series', unique=True) # 这里创建series索引仅为了去重，attrs的unique设为True会出错
        except Exception, e:
            slack('Failed to connect mongoDB:\n{} : {}'.format(str(Exception), str(e)))

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

    def insert_meta_by_series(self, series):
        name, priceType, productPlaceOfOrigin, sellerMarket, productGrade = series.split('_')
        record = {
            'series':series,
            'attrs':[
            "名称={}".format(name),
            "产地={}".format(productPlaceOfOrigin),
            "市场={}".format(sellerMarket),
            "规格={}".format(productGrade)]
        }
        try:
            self.meta.insert(record)
        except DuplicateKeyError as e:
            print (e)