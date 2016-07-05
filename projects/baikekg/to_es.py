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
from hzlib.libfile import read_file_iter, write_file
from es.es_api import get_esconfig, batch_init, run_esbulk_rows, gen_es_id
from fudan_attr import get_entity_avps_results
from filter_lib import regdropbrackets
from load_alias import get_all_aliases

DIR = '/Users/bishop/百度云同步盘/'
BATCH = 2000
ENV = 'local'
# http://localhost:9200/fudankg0630/fudankg_faq/_search?q=entity:%E5%A4%8D%E6%97%A6
ES_DATASET_CONFIG = {
        "description": "复旦百科实体属性值0705",
        "es_index": "fudankg0705",
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


def send_definition_to_es(data, field='definition', fudan=False):
    pairs = []
    count = 0

    for entity, info in data.iteritems():
        if field is None:
            definition = info.strip()
        else:
            if field not in info:
                continue
            definition = info[field].strip()

        definition_short = summary(definition, fudan=fudan)
        if fudan:
            values = [definition] if definition == definition_short else [definition_short, definition.split(u'|||')]
        else:
            values = [definition] if definition == definition_short else [definition_short, definition]

        if fudan:
            if 'alias' in info:
                pairs.append( fudan_ea_to_json(entity, '定义', '定义', 'definition', values, info['category'], info['alias']) )
            else:
                pairs.append( fudan_ea_to_json(entity, '定义', '定义', 'definition', values, info['category']) )
        else:
            pairs.append( ea_to_json(entity, '定义', '定义', 'definition', values) )
        count += 1

        if len(pairs) > BATCH:
            sendto_es(pairs)
            pairs = []
            print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if pairs:
        sendto_es(pairs)


def fudan_ea_to_json(entity, attribute, attribute_name, extra_tag, values, category=None, alias=[]):
    """
    :param entity: type(entity) is unicode
    """
    tags = [entity, entity.lower(), entity.upper(), extra_tag]
    entity_name = entity

    tags.extend(alias)
    m = regdropbrackets.match(entity)
    if m:
        entity_name = m.group(1)
        tags.append(entity_name.lower())
        tags.append(entity_name.upper())

    eid = gen_es_id('{}__{}'.format(entity.encode('utf-8'), attribute))

    # entity(index: yes) used for full text retrieval, tags(not_analyzed) used for exactly match
    ret = {
        'id': eid,
        'entity': entity,
        'entity_name': entity_name,
        'attribute': attribute,
        'attribute_name': attribute_name,
        'value': values[0],
        'values': values,
        'tags': list(set(tags)),
    }
    if category:
        ret.update({'category': category})
    return ret


def ea_to_json(entity, attribute, attribute_name, extra_tag, values):
    """
    :param entity: type(entity) is unicode
    """

    tags = [entity, entity.lower(), entity.upper(), extra_tag]
    alias = get_all_aliases(entity)
    if alias:
        tags.extend(list(alias))
#    alias_mapping = load_alias_mapping()
#    if entity in alias_mapping:
#        tags.extend(alias_mapping[entity])

    entity_name = entity

    m = regdropbrackets.match(entity)
    if m:
        entity_name = m.group(1)
        tags.append(entity_name.lower())
        tags.append(entity_name.upper())

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


def summary(text, fudan=False):
    if fudan:
        if u'|||' in text:
            return text.split(u'|||', 1)[0]
        else:
            return text

    idx = text.find("。")
    if idx > 0:
        return text[:text.index("。")+1]
    else:
        return text


def load_zgdbk_info(dirname='.'):
    fname = os.path.join(dirname, 'zgdbk_entity_info.txt')
    send_definition_to_es( read_file_iter(fname, jsn=True), field=None )


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


