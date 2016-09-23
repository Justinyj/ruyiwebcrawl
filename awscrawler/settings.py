#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import os

ENV = os.environ.get('ENV', 'DEV')
if ENV == '':
    ENV = 'DEV'

envs = {
    'DEV': {
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'CACHE_SERVER': 'http://192.168.1.179:8000',
        'REGION_NAME': 'us-west-1',
    },
    'PRODUCTION': {
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://172.31.19.253:6379/1/dQm*s5wdtC)m2AuZ',
        'QUEUE_REDIS': 'redis://172.31.19.253:6379/2/dQm*s5wdtC)m2AuZ',
        'CACHE_REDIS': [
            'redis://172.31.19.253:6379/0/dQm*s5wdtC)m2AuZ',
        ],

        'CACHE_SERVER': 'http://172.31.20.248:8000',
        'REGION_NAME': 'ap-northeast-1',
    },
    'TEST': {
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://172.31.1.59:6379/1',
        'QUEUE_REDIS': 'redis://172.31.1.59:6379/2',
        'CACHE_REDIS': [
            'redis://172.31.1.59:6379/0',
        ],

        'CACHE_SERVER': 'http://172.31.1.59:8000',
        'REGION_NAME': 'us-west-1',
    },
    'XIAMI':{
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://172.31.13.36:6379/1/dQm*s5wdtC)m2AuZ',
        'QUEUE_REDIS': 'redis://172.31.13.36:6379/2/dQm*s5wdtC)m2AuZ',
        'CACHE_REDIS': [
            'redis://172.31.13.36:6379/0/dQm*s5wdtC)m2AuZ',
        ],

        'CACHE_SERVER': 'http://172.31.13.36:8000',
        'REGION_NAME': 'cn-north-1',
    }
}

for key, value in envs.get(ENV, envs['DEV']).items():
    globals()[key] = value

