#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time
import lxml.html
from collections import Counter

gcounter = Counter()

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
    'Host': 'data.eastmoney.com',
}


def make_session():
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
    session.headers = HEADERS
    return session

def get_gonggao():
    session = make_session()

    refer = None
    content_urls = []
    for i in xrange(1, 35349):
        url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'.format(i)
        if refer is None:
            refer = url
        session.headers.update({'Referer': refer})
        try:
            resp = session.get(url)
            if resp.status_code != 200 or resp.url != url:
                gcounter['error'] += 1
                continue
            tree = lxml.html.fromstring( r.content.decode('gb18030') )
            urls = tree.xpath('//td[@class="title"]/a/@href')
            if urls == []:
                gcounter['error'] += 1
            for url in urls:
                content_urls.append( urlparse.urljoin('http://data.eastmoney.com/', url) )

        except Exception as e:
            gcounter['error'] += 1
            print(e)


