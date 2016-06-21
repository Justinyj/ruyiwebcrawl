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

GAP = 5
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


def load_page_no():
    persistent_page_no_file = 'persistent_page_no_file.txt'
    if not os.path.exists(persistent_page_no_file):
        return 0
    with open(persistent_page_no_file) as fd:
        page = fd.read().strip()
        if page == '':
            return 0
    return int(page)


def write_page_no(pageno):
    persistent_page_no_file = 'persistent_page_no_file.txt'
    with open(persistent_page_no_file, 'w') as fd:
        fd.write(str(pageno))


def make_session():
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
    session.headers = HEADERS
    return session


def get_gonggao(pageno):
    session = make_session()
    tail = 35349
    notice_urls = 'notice_urls.txt'
    head = pageno + 1

    refer = None
    fd = open('error_page.txt', 'a')
    with open(notice_urls, 'a') as urlfd:
        for i in xrange(head, tail):
            url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'.format(i)
            if refer is None:
                refer = url
            session.headers.update({'Referer': refer})
            try:
                for _ in range(3):
                    resp = session.get(url)
                    time.sleep(GAP)
                    if resp.status_code != 200 or resp.url != url:
                        continue
                    tree = lxml.html.fromstring( resp.content.decode('gb18030') )
                    urls = tree.xpath('//td[@class="title"]/a/@href')
                    if urls == []:
                        continue
                    else:
                        break
                else:
                    gcounter['error'] += 1
                    fd.write(url)
                    fd.write('\n')
                for url in urls:
                    urlfd.write( urlparse.urljoin('http://data.eastmoney.com/', url) )
                    urlfd.write('\n')

            except Exception as e:
                gcounter['error'] += 1
                print(e)
            write_page_no(i)
    fd.close()


pageno = load_page_no()
get_gonggao(pageno)
