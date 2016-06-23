#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import random
import json
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from collections import Counter
from operator import itemgetter

from downloader.downloader_wrapper import DownloadWrapper
from hzlib.libfile import writeExcel

class FudanAttr(object):

    batch_id = {
        'entity': 'fudankg-entity-20160623',
        'avp': 'fudankg-avp-20160623',
    }

    def __init__(self):
        self.downloader = DownloadWrapper('http://192.168.1.179:8000')
        self.attr_counter = Counter()


    def fudan_entities(self, word):
        if isinstance(word, unicode):
            word = word.encode('utf-8')

        entities_api = 'http://kw.fudan.edu.cn/cndbpedia/api/entity?mention={}'
        content = self.downloader.downloader_wrapper(
                entities_api.format(urllib.quote(word)),
                self.batch_id['entity'],
                gap=0,
                encoding='utf-8',
                )
        return json.loads(content)[u'entity']


    def fudan_attrvalue(self, entity):
        if isinstance(entity, unicode):
            entity = entity.encode('utf-8')

        avpair_api = 'http://kw.fudan.edu.cn/cndbpedia/api/entityAVP?entity={}'
        content = self.downloader.downloader_wrapper(
                avpair_api.format(urllib.quote(entity)),
                self.batch_id['avp'],
                gap=0,
                encoding='utf-8',
                )
        return json.loads(content).values()[0]


    def fudan_attr_count(self, result):
        """[ (word, entity, [(attr, value), (attr, value), ...])
           ]
        """
        for word, entity, avps in result:
              for a,v in avps:
                self.attr_counter[a] += 1
        count = sorted(self.attr_counter.items(), key=itemgetter(1), reverse=True)
        print( json.dumps(count, ensure_ascii=False, indent=4) )


    def fudan_gen_excel(self, result):
        items = []
        keys = ['word', 'entity', 'attribute', 'value']
        filename = 'fudan_eav.xlsx'

        for word, entity, avps in result:
              for a,v in avps:
                items.append({'word': word.decode('utf-8'),
                              'entity': entity,
                              'attribute': a,
                              'value': v})

        writeExcel(items, keys, filename)




    def prepare_entities(self, entities_fname='entities_0623.txt'):
        words = []
        with open(entities_fname) as fd:
            for line in fd:
                line = line.strip()
                if line == '':
                    continue
                words.append(line)

        picked_words = self.pick_some_words(words, 1000)
        self.save_picked_words(picked_words)


    def pick_some_words(self, words, num=1000):
        picked_words = []
        for i in range(num):
            picked_words.append( words[random.randint(1, len(words))] )
        return picked_words


    def save_picked_words(self, words):
        words.extend(['长江', '熊二', '杨绛先生'])
        with open('picked_thousand_words.txt', 'w') as fd:
            fd.write('\n'.join( list(set(words)) ))


def generate_thousand_words():
    obj = FudanAttr()
    obj.prepare_entities()

def generate_entity_avp_excel():
    result = []
    obj = FudanAttr()

    with open('picked_thousand_words.txt') as fd:
        for word in fd:
            word = word.strip()
            for entity in obj.fudan_entities(word):
                result.append((word, entity, obj.fudan_attrvalue(entity)))

    obj.fudan_attr_count(result)
    obj.fudan_gen_excel(result)


if __name__ == '__main__':
    generate_entity_avp_excel()
