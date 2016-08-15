#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from es.es_api import get_esconfig, batch_init, run_esbulk_rows

ENV = 'local'
CONFIG = {
    'local': {'CACHESERVER': 'http://192.168.1.179:8000'},
    'prod': {'CACHESERVER': 'http://127.0.0.1:8000'},
}

ES_DATASET_CONFIG = {
        'description': 'hprice',
        'es_index': 'hprice',
        'es_type': 'metrialprice',
        'filepath_mapping': os.path.abspath(os.path.dirname(__file__)) + '/' + 'price_schema.json'
}

batch_init(get_esconfig(ENV), [ES_DATASET_CONFIG])

def sendto_es(jsons):
    esconfig = get_esconfig(ENV)
    run_esbulk_rows(jsons, "index", esconfig, ES_DATASET_CONFIG)

