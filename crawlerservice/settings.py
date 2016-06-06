#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import os

ENV = os.environ.get('ENV', 'DEV')
if ENV == '':
    ENV = 'DEV'

envs = {
    'DEV': {
        'DBNAME': 'crawlercache',
        'DBUSER': 'postgres',
        'DBPASS': '1qaz2wsx',
        'DBHOST': '127.0.0.1',
        'DBPORT': 5432,

        'CACHEPAGE': 's3', # ufile, fs, pg, qiniu, s3
        'REGION_NAME': 'ap-northeast-1',
        'FSCACHEDIR': '/data/crawlercache/',
        'CONCURRENT_NUM': 200,

        # these three for prefetch
        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        # these two for fetch
        'PROXY_SERVER': 'http://127.0.0.1:8001',
        'CACHE_SERVER': 'http://127.0.0.1:8000',
    },
    'PRODUCTION': {
        'DBNAME': 'crawlercache',
        'DBUSER': 'postgres',
        'DBPASS': '1qaz2wsx',
        'DBHOST': '127.0.0.1',
        'DBPORT': 5432,

        'CACHEPAGE': 'ufile', # ufile, fs, pg, qiniu
        'FSCACHEDIR': '/data/crawler_file_cache/',
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'PROXY_SERVER': 'http://127.0.0.1:8001',
        'CACHE_SERVER': 'http://127.0.0.1:8000',
    },
    'TEST': {
        'DBNAME': 'crawlercache',
        'DBUSER': 'postgres',
        'DBPASS': '1qaz2wsx',
        'DBHOST': '127.0.0.1',
        'DBPORT': 5432,

        'CACHEPAGE': 'fs', # ufile, fs, pg, qiniu
        'FSCACHEDIR': '/data/crawler_file_cache/',
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'PROXY_SERVER': 'http://127.0.0.1:8001',
        'CACHE_SERVER': 'http://127.0.0.1:8000',
    },
    'ZHIDAO': {
        'DBNAME': 'crawlercache',
        'DBUSER': 'postgres',
        'DBPASS': '1qaz2wsx',
        'DBHOST': '127.0.0.1',
        'DBPORT': 5432,

        'CACHEPAGE': 's3', # ufile, fs, pg, qiniu
        'REGION_NAME': 'us-west-1',
        'FSCACHEDIR': '/data/crawler_file_cache/',
        'CONCURRENT_NUM': 200,

        'RECORD_REDIS': 'redis://localhost:6379/1',
        'QUEUE_REDIS': 'redis://localhost:6379/2',
        'CACHE_REDIS': [
            'redis://localhost:6379/0',
        ],

        'PROXY_SERVER': 'http://127.0.0.1:8001',
        'CACHE_SERVER': 'http://127.0.0.1:8000',
    }
}

for key, value in envs.get(ENV, envs['DEV']).items():
    globals()[key] = value
