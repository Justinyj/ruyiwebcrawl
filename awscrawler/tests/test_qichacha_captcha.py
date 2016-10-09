#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time
import urllib
from collections import Counter

GAP = 1
gcounter = Counter()

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
    'Host': 'www.qichacha.com',
    'Cookie': 'gr_user_id=f0a0a3c5-5298-4274-89a4-081a4ff9e862; _uab_collina=147332984299621423125018; _umdata=0823A424438F76ABAA14D135C311D13E9AE17292FE7E9C5F690E31AAE88C8B67CCD696260DB796F68DB103625F35CF2A3F421E980413046BD2CACCD22AF0E14EA2356AF0D2D1E9DF35774D85F5E81DFC470F2C11488AA47999ECF36F46866D2A; PHPSESSID=24bam7qb43c8g5og2ke8s1cjd7; gr_session_id_9c1eb7420511f8b2=093ac0ab-cebe-4309-bf21-4e65bd2733b1; CNZZDATA1254842228=1369801759-1471331946-%7C1475989400'
}


session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
session.headers = HEADERS

def test_qichach_search():

    with open('test_qichacha_captcha.txt') as fd:
        for i, line in enumerate(fd):

            url = 'http://www.qichacha.com/search?key={}&index=0'
            url = url.format(urllib.quote(line.strip()))
            resp = session.get(url, timeout=10)
            print(i, resp.url)
            if url != resp.url:
                gcounter['error'] += 1
            time.sleep(GAP)
            gcounter['total'] += 1

test_qichach_search()
