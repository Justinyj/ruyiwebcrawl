#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from pymongo import MongoClient
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Extraction(object):
    def __init__(self):
        client = MongoClient('localhost', 27018)
        self.news_collection = client['kgbrain']['news']
        self.entities_collection = client['kgbrain']['entities']

    def data_flow(self):
        drop_list = [u'', u'-']
        for news in self.news_collection.find():
            for item in news[u'claims']:
                if item[u'p'] == u'标题':
                    seg_list = set([i for i in self.cut(item[u'o']) if i not in drop_list])
                    print(u'entities: ' + u'/ '.join(map(str, seg_list.intersection(self.entities))))
                    print(u"title: " + u"/ ".join(seg_list))
                elif item[u'p'] == u'正文':
                    seg_list = set([i for i in self.cut(item[u'o']) if i not in drop_list])
                    print(u'entities: ' + u'/ '.join(map(str, seg_list.intersection(self.entities))))
                    print(u"content: " + u"/ ".join(seg_list))
                elif item[u'p'] == u'日期':
                    pass

    def get_region(self):
        from region import REGION_CODE
        regions = set()
        for province, value in REGION_CODE.iteritems():
            if u"省/直辖市" == province or u"其他" == province or u"海外" == province:
                continue
            regions.add(province)
            for dummy, cities in value.iteritems():
                if dummy == u"code":
                    continue
                regions.update( cities.keys() )

        with open('world_city.txt') as fd:
            world_city = fd.read()
            countries = map(unicode, re.findall('\((.+?)\)', world_city))
            regions.update(countries)
        return regions

    def get_entities(self):
        entities = set()
        for entity in self.entities_collection.find():
            entities.update( entity['alias'] )
        return entities

    def add_entities_to_dic(self, words):
        supplements = [u'鼠鲨', u'天麻']
        import jieba
        for word in words:
            jieba.add_word(word)

        for e in supplements:
            words.update(e)
            jieba.add_word(e)

        self.entities = words
        self.jieba = jieba

    def cut(self, segment):
        seg_list = self.jieba.cut(segment, HMM=False)
        return seg_list


if __name__ == '__main__':
    extraction = Extraction()
    entities = extraction.get_entities()
    entities.update( extraction.get_region() )
    extraction.add_entities_to_dic(entities)

    extraction.data_flow()

