#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
from es.es_api import get_esconfig, batch_init, run_esbulk_rows

ENV = 'xiami'
CONFIG = {
    'local': {'CACHESERVER': 'http://192.168.1.179:8000'},
    'prod': {'CACHESERVER': 'http://127.0.0.1:8000'},
    'xiami':{'CACHESERVER': 'http://192.168.1.179:8000'}
}

ES_DATASET_CONFIG = {
        'description': 'hprice',
        'es_index': 'hprice',
        'es_type': 'materialprice',
        'filepath_mapping': os.path.abspath(os.path.dirname(__file__)) + '/' + 'price_schema.json'
}

ES_DATASET_CONFIG = {
        'description': 'clean_music_xiami_20161028',
        'es_index': 'clean_music_xiami_whole_20161028',
        'es_type': 'xiamimusic',
        'filepath_mapping': os.path.abspath(os.path.dirname(__file__)) + '/' + 'music_schema.json'
}

ES_DATASET_CONFIG_M = {
        'description': 'hprice',
        'es_index': 'hprice',
        'es_type': 'metrialproperty',
        'filepath_mapping': os.path.abspath(os.path.dirname(__file__)) + '/' + 'price_schema.json'
}

batch_init(get_esconfig(ENV), [ES_DATASET_CONFIG])
def sendto_es(jsons):
    esconfig = get_esconfig(ENV)
    run_esbulk_rows(jsons, "index", esconfig, ES_DATASET_CONFIG)

