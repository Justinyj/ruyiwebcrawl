#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import json
import os
import lxml.html


header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Host':'www.xiami.com',
    #'Referer':'http://www.xiami.com/search/artist/page/2?spm=a1z1s.3521877.23310097.92.R2W4F4&key=%2A&category=-1',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
}

path = '/Users/bishop/Documents/海知智能/xiami'

def download_all_artists():
    global path
    gap = 0
    url  = 'http://www.xiami.com/search/artist/page/{}?spm=a1z1s.3521877.0.0.hqrWay&key=%2A&category=-1'
    counter = { 'success': 0, 'failed': 0 }

    for page in range(1, 7783):
        content = requests.get(url.format(page), headers = header).text
        if u'位艺人符合' in content:
            counter['success'] += 1
            with open(os.path.join(path, '{}.txt'.format(page)),'w') as f:
                f.write(content.encode('utf-8') + '\n')
        else:
            counter['failed'] += 1
        time.sleep(gap)
    print 'error rate:{}' .format(counter['failed'] / (counter['success'] + counter['failed'] ))


def parse_all_artists():
    """
    {
        "singer_title": "憂歌団",
        "singer_id": "78925",
        "singer_region": "Japan 日本",
        "singer_name": "(优歌团 ゆうかだん)"
    }
    """
    global path

    for f in os.listdir(path):
        if f.endswith('.py') or f.startswith('.'):
            continue
        fname = os.path.join(path, f) 
        with open(fname) as fd:
            cont = fd.read()
        html = lxml.html.fromstring(cont)
        for item in html.cssselect('.artistBlock_list .hor-list-item'):
            title = item.cssselect('.name > .title')[0]
            singer_region = item.cssselect('.singer_region')
            singer_region = singer_region[0].get('title') if singer_region else None
            singer_name = item.cssselect('.singer_names')
            singer_name = singer_name[0].text_content() if singer_name else None

            singer = {
                'singer_id': title.get('href').rsplit('/', 1)[-1],
                'singer_title':  title.get('title'),
                'singer_name': singer_name,
                'singer_region': singer_region
            }
            print(json.dumps(singer, ensure_ascii=False, indent=4))

