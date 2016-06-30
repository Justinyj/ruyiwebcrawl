#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from hzlib.libfile import read_file_iter, write_file
from filter_lib import regdisambiguation
from entities_sort import db_data_unique


def load_dbpedia():
    data = {}
    for line in read_file_iter('merge_step_5_simplified.json', jsn=True):
        for key, value in line.items():
            entity = value[u'resource_label'].encode('utf-8')
            data[entity] = {}

            if u'short_abstract' in value:
                data[entity]['definition'] = value[u'short_abstract']
                value.pop(u'short_abstract')

            if u'resource_alias' in value:
                data[entity]['aliases'] = value[u'resource_alias']
                value.pop(u'resource_alias')

            data[entity]['attributes'] = value


def load_wikidata():
    data = {}
    for jsn in read_file_iter('wikidata_zh_simplified.json', jsn=True):
        m = regdisambiguation.match(jsn[u'chinese_label'])
        item = m.group(1) if m else jsn[u'chinese_label']
        entity = item.strip().encode('utf-8')
        data[entity] = {}

        if u'chinese_aliases' in jsn:
            data[entity]['aliases'] = jsn[u'chinese_aliases']
            jsn.pop(u'chinese_aliases')

        data[entity]['attributes'] = jsn


if __name__ == '__main__':
    dbpediadata = load_dbpedia()
    wikidata = load_wikidata()
    inter = db_data_unique()

    import random
    import json
    compare = {}
    for i in range(20):
        entity = random.choice(inter)
        if entity in dbpediadata and entity in wikidata: 
            compare[entity] = {
                'dbpedia': dbpediadata[entity],
                'wikidata': wikidata[entity],
            }

    json.dump(compare, ensure_ascii=False, indent=4)
