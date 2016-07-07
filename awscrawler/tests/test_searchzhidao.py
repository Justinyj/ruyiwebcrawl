#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
import requests
import urlparse
import time
import lxml.html
from collections import Counter

GAP = 0
gcounter = Counter()

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
    'Host': 'zhidao.baidu.com',
}

session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
session.headers = HEADERS

def test_searchzhidao():
    url = 'http://zhidao.baidu.com/search?word=%CE%AA%CA%B2%C3%B4%CC%EC%BB%E1%CF%C2%D3%EA'
    total = 500
    for i in xrange(total):
        resp = session.get(url, timeout=10)
        print('\n', resp.headers['Content-Type'], len(resp.content)) # normally: 'text/html'
        print(resp.status_code, resp.url)
        if resp.status_code != 200 or resp.url != url:
            gcounter['error'] += 1
        time.sleep(GAP)
        print('Error percentage: {}'.format(gcounter['error'] / total))

test_searchzhidao()
