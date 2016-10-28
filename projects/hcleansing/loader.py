#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import re
import requests
import os

from pymongo.errors import DuplicateKeyError
from urlparse import urlparse
from pymongo import MongoClient
from datetime import datetime


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
        self.news = db['news']
        self.pipe_line = pipeLine()

        try:
            self.entity.create_index('gid', unique=True)
            self.node.create_index('gid', unique=True)
            self.node.create_index('series', unique=False)
            self.node.create_index('tags', unique=False)
            self.node.create_index('recordDate', unique=False)
            self.meta.create_index('attrs', unique=False)
            self.meta.create_index('series', unique=True) # 这里创建series索引仅为了去重，attrs的unique设为True会出错
            self.news.create_index('tags', unique=False)
            self.news.create_index('gid', unique=True)
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
        tags = series.split('_')
        keys = [u'名称', u'价格类型', u'产地', u'市场', u'规格'] # 这个前缀列表可用的前提是假设series中字段都按照规定的顺序排列
        record = {
            'series':series,
            'createdTime': datetime.utcnow(),
            'updatedTime': datetime.utcnow()
        }
        for index in range(5):
            if tags[index]:
                record[keys[index]] = tags[index]
        record[u'规格'] = [record[u'规格']]
        self.pipe_line.clean_product_place(tags[2], record)

        try:
            self.meta.insert(record)
        except DuplicateKeyError as e:
            print (e)

    def set_price_index(self, data_series, name, source):
        # 为了导出价格数据索引
        data = {
            "data_series":  data_series,
            "product": name, 
            "source": source,
        }
        with open('price_index_list.txt', 'a') as f:            # 不同的清洗脚本都要导出，所以用append模式，注意每次导出索引时删除旧文件
            f.write(json.dumps(data, ensure_ascii = False) + '\n')

class pipeLine(object):
    def __init__(self, filename='productPlaceMapping.json'):  # 生成所有产地方法： db.pricemeta.distinct("attrs.1")   
        product_place_mapping_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(product_place_mapping_path, 'r') as f:
            self.product_place_mapping = json.load(f)

    def is_place(self, word):
        place_list = [u'国内', u'国外', u'较广']                             #   这些是mapping文件中所有属于产地的value字段
        return word in place_list

    def clean_product_place(self, product_place, item):                          #    这个tags可能是元数据的record格式，也可能是price record的tags格式，会在此方法内进行区分
        mapped_result_list = self.product_place_mapping.get(product_place, None)
        if not mapped_result_list:
            return
        if isinstance(item, dict):
            for mapped_result in mapped_result_list:
                if self.is_place(mapped_result):                                # 不是产地就是规格，暂时不考虑其他情况
                    print (u'国家={}'.format(mapped_result))
                    item[u'国家'] = mapped_result
                else:
                    print (u'规格={}'.format(mapped_result))
                    item[u'规格'].append(mapped_result)
        else:
            item.extend(mapped_result_list)
