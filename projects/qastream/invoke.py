#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from zhidao.zhidao_scheduler import Scheduler


CACHESERVER = 'http://192.168.1.179:8000'
ES_INDEX = "zhidao"

s = Scheduler.instance(CACHESERVER)
ret = s.run('晚上吃什么有益健康', gap=3)
print(ret)

mappings = {
    "es_url": "http://nlp.ruyi.ai:9200",
    "es_user": "es_ruyi",
    "es_pass": "ruyiruyies",
    "es_auth": "Basic ZXNfcnV5aTpydXlpcnV5aWVz"
}

run_es_create_index(filename_esconfig, dataset["es_index"])
run_es_create_mapping(filename_esconfig, dataset["es_index"], dataset["es_type"], mappings)

ES_DATASETS = [
    {
        "description": "百度知道002",
        "es_index": ES_INDEX,
        "es_type": "zhidao_faq",
        "filepath_mapping": "qa_es_schema.json",
        "filepath": "baiduzhidao_79.esdata"
    },
]

es_api.run_batch(ES_DATASETS, ES_INDEX, option, sys.argv)



MSG_HELP = '''

# delete index
curl -XDELETE -u es_ruyi:ruyiruyies http://nlp.ruyi.ai:9200/{es_index}

# init index
python python/baiduzhidao/run_esdata.py init-prod esdata

python python/baiduzhidao/run_esdata.py stat

# upload prod
python python/baiduzhidao/run_esdata.py upload-prod esdata


'''.format(es_index=ES_INDEX)
