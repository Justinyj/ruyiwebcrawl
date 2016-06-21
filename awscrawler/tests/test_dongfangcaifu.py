#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time
import lxml.html
from collections import Counter

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'Host': 'data.eastmoney.com',
}


url = 'http://data.eastmoney.com/notice/20150509/2Wvl2WNLCVR2KS.html'
url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=35262'
gcounter = Counter()

def func():
    global url, gcounter

    for i in range(500):
        print(gcounter['error'], gcounter['count'])
        time.sleep(3)
        gcounter['count'] += 1

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200 or r.url != url:
                gcounter['error'] += 1
                print(r.status_code, r.url, r.headers)
            else:
                tree = lxml.html.fromstring( r.content.decode('gb18030') )
                urls = tree.xpath('//td[@class="title"]/a/@href')
                if urls == []:
                    gcounter['error'] += 1
                    print(r.status_code, r.url, r.headers)
        except Exception as e:
            gcounter['error'] += 1
            print(e)

    print('result: ', gcounter['error'], gcounter['count'])

func()
