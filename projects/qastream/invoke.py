#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from zhidao.zhidao_scheduler import Scheduler


CACHESERVER = 'http://192.168.1.179:8000'

s = Scheduler.instance(CACHESERVER)
ret = s.run('晚上吃什么有益健康', gap=3)
print(ret)




from es.es_api import get_esconfig, batch_init, run_esbulk_rows

ES_INDEX = "zhidao"
ES_DATASET_CONFIG = {
        "description": "百度知道002",
        "es_index": ES_INDEX,
        "es_type": "zhidao_faq",
        "filepath_mapping": "qa_es_schema.json"
}

config_option = "local"
esconfig = get_esconfig(config_option)
batch_init(esconfig, [ES_DATASET_CONFIG])
run_esbulk_rows(items, "index", esconfig, ES_DATASET_CONFIG)

