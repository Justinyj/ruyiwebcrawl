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

        'CACHEPAGE': 'fs', # fs, pg, qiniu
        'FSCACHEDIR': '/data/crawler_file_cache/',
        'FSCACHEDIR': '/tmp',
    },
}

for key, value in envs.get(ENV, envs['DEV']).items():
    globals()[key] = value
