#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os

ENV = os.environ.get('ENV', 'DEV')
if ENV == '':
    ENV = 'ENV'

envs = {
    'DEV': {
        'CACHESERVER': 'http://192.168.1.179:8000',
        'PROXYSERVER': 'http://192.168.1.179:8888',
        'CRAWL_GAP': 5,
    },
}

for k, v in envs.get(ENV, envs['DEV']).items():
    globals()[k] = v
