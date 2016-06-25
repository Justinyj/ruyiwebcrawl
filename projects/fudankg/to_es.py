#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json
import os
import re
from collections import defaultdict
from datetime import datetime

from es.es_api import get_esconfig, batch_init, run_esbulk_rows, gen_es_id
from fudan_attr import get_entity_avps_results

ENV = 'prod'
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
        eavp = parse_one_entity(entity, avps)
        eavps.extend(eavp)
    return eavps


def sendto_es(eavps):
    esconfig = get_esconfig(ENV)
    # post 'http://localhost:9200/_bulk'
    run_esbulk_rows(eavps, "index", esconfig, ES_DATASET_CONFIG)


def load_json_files(dirname='.'):
    eavps = []
    count = 0

    for f in os.listdir(dirname):
        with open(os.path.join(dirname, f)) as fd:
            for entity, avps in json.load(fd).items():
                eavp = parse_one_entity(entity, avps)
                eavps.extend(eavp)

        count += 1
        if len(eavps) > 1000:
            sendto_es(eavps)
            eavps = []
            print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if eavps:
        sendto_es(eavps)


def parse_one_entity(entity, avps):
    eavp = []
    attr_values = defaultdict(list)

    for a, v in avps:
        attr_values[a].append(v)
    for a, v in attr_values.iteritems():
        eid = gen_es_id('{}__{}'.format(entity.encode('utf-8'),
                                        a.encode('utf-8')))
        if a == u'中文名':
            continue

        attribute_hit = [a]
        tags = [entity]
        m = re.compile(u'(.+?)(\(|（).+(\)|）)').match(entity)
        if m:
            tags.append(m.group(1))
        # entity(index: yes) used for full text retrieval, tags(not_analyzed) used for exactly match
        eavp.append({'id': eid,
                      'entity': entity,
                      'attribute': a,
                      'values': v,
                      'value': v[0],
                      'tags': tags,
                      'attribute_hit': attribute_hit})
    return eavp


def load_zgdbk_info():
    einfos = []
    count = 0

    with open('zgdbk_entity_info.txt') as fd:
        for line in fd:
            js = json.loads(line.strip())
            for entity, info in js.items():

                tags = [entity, '定义']
                m = re.compile(u'(.+?)(\(|（).+(\)|）)').match(entity)
                if m:
                    tags.append(m.group(1))
                eid = gen_es_id('{}__{}'.format(entity.encode('utf-8'), '定义'))

                einfos.append({
                        'id': eid,
                        'entity': entity,
                        'attribute': '定义',
                        'value': info,
                        'values': [info],
                        'tags': tags})
            count += 1
            if len(einfos) > 1000:
                sendto_es(einfos)
                einfos = []
                print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if einfos:
        sendto_es(einfos)


if __name__ == '__main__':
#    load_json_files('/Users/bishop/百度云同步盘/fudankg-json')

    load_zgdbk_info()
