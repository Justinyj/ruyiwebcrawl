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

        'CACHE_SERVER': 'http://127.0.0.1:8000',
        'REGION_NAME': 'us-west-1',
    },
    'PRODUCTION': {
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'CACHE_SERVER': 'http://127.0.0.1:8000',
        'REGION_NAME': 'ap-northeast-1',
    },
    'TEST': {
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'CACHE_SERVER': 'http://172.31.23.63:8000',
        'REGION_NAME': 'us-west-1',
    }
}

for key, value in envs.get(ENV, envs['DEV']).items():
    globals()[key] = value

