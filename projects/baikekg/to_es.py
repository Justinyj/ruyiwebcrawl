#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json
import os
import re
from datetime import datetime
from operator import itemgetter
from collections import defaultdict, Counter

from hzlib.libfile import readExcel
from es.es_api import get_esconfig, batch_init, run_esbulk_rows, gen_es_id
from fudan_attr import get_entity_avps_results
from filter_lib import regfdentitysearch

DIR = '/Users/bishop/百度云同步盘/'
BATCH = 2000
ENV = 'local'
# http://localhost:9200/fudankg0623/fudankg_faq/_search?q=entity:%E5%A4%8D%E6%97%A6
ES_DATASET_CONFIG = {
        "description": "复旦百科实体属性值0623",
        "es_index": "fudankg0623",
        "es_type": "fudankg_faq",
        "filepath_mapping": os.path.abspath(os.path.dirname(__file__)) +"/"+"fudankg_es_schema.json"
}

# search es_index 'http://localhost:9200/fudankg0623/_search?', no hits
# then post 'http://localhost:9200/fudankg0623'
# get 'http://localhost:9200/fudankg0623/fudankg_faq/_mapping', empty return
# then put 'http://localhost:9200/fudankg0623/fudankg_faq/_mapping?pretty' with json
batch_init(get_esconfig(ENV), [ES_DATASET_CONFIG])

def insert():
    results = get_entity_avps_results()
    eavps = []

    for word, entity, avps in results:
        eavp = parse_fudan_entity(entity, avps)
        eavps.extend(eavp)
    return eavps



def sendto_es(eavps):
    esconfig = get_esconfig(ENV)
    # post 'http://localhost:9200/_bulk'
    run_esbulk_rows(eavps, "index", esconfig, ES_DATASET_CONFIG)


def load_fudan_json_files(dirname='.'):
    eavps = []
    count = 0

    for f in os.listdir(dirname):
        with open(os.path.join(dirname, f)) as fd:
            for entity, avps in json.load(fd).items():
                eavp = parse_fudan_entity(entity, avps)
                eavps.extend(eavp)

        count += 1
        if len(eavps) > BATCH:
            sendto_es(eavps)
            eavps = []
            print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if eavps:
        sendto_es(eavps)

def load_attribute_mapping():
    if not hasattr(load_attribute_mapping, '_attr'):
        attribute_mapping = {}
        items = readExcel(['实体', '属性标准名', 'FD属性', '多种属性表达'], '/Users/bishop/百度云同步盘/baike_attribute.xls', 1)
        for i in items['Sheet1']:
            attribute_mapping[ i['FD属性'] ] = i['多种属性表达']
        setattr(load_attribute_mapping, '_attr', attribute_mapping)
    return load_attribute_mapping._attr

def parse_fudan_entity(entity, avps):
    eavp = []
    attr_values = defaultdict(list)

    attribute_mapping = load_attribute_mapping()

    for a, v in avps:
        attr_values[a].append(v)

    for a, v in attr_values.iteritems():
        if a == u'中文名':
            continue

        attribute = a.encode('utf-8')
        attribute_name = attribute_mapping.get(a, attribute) # mapping is unicode
        eavp.append( ea_to_json(entity, attribute, attribute_name, 'attribute', v) )
    return eavp


def ea_to_json(entity, attribute, attribute_name, extra_tag, values):
    """
    :param entity: type(entity) is unicode
    """

    tags = [entity, extra_tag]
    alias_mapping = load_alias_mapping()
    if entity in alias_mapping:
        tags.extend(alias_mapping[entity])

    entity_name = entity

    m = regfdentitysearch.match(entity)
    if m:
        tags.append(m.group(1))
        entity_name = m.group(1)

    eid = gen_es_id('{}__{}'.format(entity.encode('utf-8'), attribute))

    # entity(index: yes) used for full text retrieval, tags(not_analyzed) used for exactly match
    return {
        'id': eid,
        'entity': entity,
        'entity_name': entity_name,
        'attribute': attribute,
        'attribute_name': attribute_name,
        'value': values[0],
        'values': values,
        'tags': list(set(tags))
    }


def summary(text):
    idx = text.find("。")
    if idx > 0:
        return text[:text.index("。")+1]
    else:
        return text

def load_zgdbk_info(dirname='.'):
    einfos = []
    count = 0

    fname = os.path.join(dirname, 'zgdbk_entity_info.txt')
    with open(fname) as fd:
        for line in fd:
            js = json.loads(line.strip())
            for entity, info in js.items():
                info = info.strip()
                info_short = summary(info)
                einfos.append( ea_to_json(entity, '定义', '定义', 'definition', [info_short, info]) )

            count += 1
            if len(einfos) > BATCH:
                sendto_es(einfos)
                einfos = []
                print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if einfos:
        sendto_es(einfos)


def load_alias_mapping():
    if not hasattr(load_alias_mapping, '_mapping'):
        entity_alias_mapping = {}

        infile = os.path.join(DIR, 'zgdbk_entity_with_alias.txt')
        with open(infile) as fd:
            for line in fd:
                line = line.strip()
                words = line.split('\t')
                if len(words) > 1:
                    entity_alias_mapping[words[0].decode('utf-8')] = words[1:]
        setattr(load_alias_mapping, '_mapping', entity_alias_mapping)
    return load_alias_mapping._mapping


if __name__ == '__main__':

    load_fudan_json_files(DIR + 'fudankg-json')
    load_zgdbk_info(DIR)


