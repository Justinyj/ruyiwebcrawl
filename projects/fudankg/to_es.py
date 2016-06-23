#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import os
import re
from collections import defaultdict

from es.es_api import get_esconfig, batch_init, run_esbulk_rows, gen_es_id
from fudan_attr import get_entity_avps_results

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
        attr_values = defaultdict(list)
        for a, v in avps:
            attr_values[a].append(v)
        for a, v in attr_values.iteritems():
            eid = gen_es_id('{}__{}'.format(entity.encode('utf-8'),
                                            a.encode('utf-8')))

            tags = [entity]
            m = re.compile(u'(.+)(\(|（).+(\)|）)').match(entity)
            if m:
                tags.append(m.group(1))
            # entity(index: yes) used for full text retrieval, tags(not_analyzed) used for exactly match
            eavps.append({'id': eid,
                          'entity': entity,
                          'attribute': a,
                          'values': v,
                          'value': v[0],
                          'tags': tags})
    return eavps

def sendto_es(eavps):
    esconfig = get_esconfig(ENV)
    # post 'http://localhost:9200/_bulk'
    run_esbulk_rows(eavps, "index", esconfig, ES_DATASET_CONFIG)

if __name__ == '__main__':
    eavps = insert()
    sendto_es(eavps)
