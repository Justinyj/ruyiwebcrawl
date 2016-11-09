#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>


import json
import urllib
import re
import urlparse
import lxml.html
import time
import requests
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from downloader.cacheperiod import CachePeriod
from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER


headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':'www.xiami.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    }

def crawl_songs_by_tag(tag):
    print tag.decode('utf-8')
    page = 1
    url_pattern = 'http://www.xiami.com/song/tag/{}/page/{}?spm=a1z1s.3521893.0.0.AUwjlw'
    ids = []
    while 1:
        url = url_pattern.format(tag, page)
        content = requests.get(url, headers=headers).text
        if page == 5 or u'找不到与标' in content:
            break
        dom = lxml.html.fromstring(content)
        hrefs = dom.xpath('//td[@class="song_name"]/a[1]/@href')
        for href in hrefs:
            song_id = re.findall('\d+', href)[0]
            ids.append(song_id)
        page += 1
    for songid in ids[:30]:
        update_tags_by_id(songid, [tag])
    result = {
        tag: ids,
    }
    # with open('tagggggggg.txt', 'a') as f:
        # f.write(json.dumps(result, ensure_ascii=False) + '\n')


def update_tags_by_id(id,tag):
    # print id, len(tag)
    if not tag:
        print id
    url_pattern = 'http://106.75.27.226/clean_music_xiami_whole_20161028/xiamimusic/{}'
    item = json.loads(requests.get(url_pattern.format(id)).text)
    if not item['found']:
        return
    tags = item[u'_source']['tags']
    # for index in range(len(tags))[::-1]:
        # if tags[index].startswith(u'TN:'):
            # tags.pop(index)
    tag = [u'TN:{}'.format(ele) for ele in tag]
    tags.extend(tag)
    tags = list(set(tags))
    update_url = url_pattern.format('{}/_update'.format(id))
    data = {
            'doc':{
                'tags':tags,
            }
    }
    data_string =  json.dumps(data, ensure_ascii=False)
    print requests.post(update_url,data=data_string.encode('utf-8')).text

def main(filename):
    tags = []
    with open(filename, 'r') as f:
        for line in f:
            tags.append(line.strip())
    for tag in tags:
        crawl_songs_by_tag(tag)

tags = [u'法语']
for tag in tags:
    crawl_songs_by_tag(tag)
def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))
    tag = url
    page = 1
    url_pattern = 'http://www.xiami.com/song/tag/{}/page/{}?spm=a1z1s.3521893.0.0.AUwjlw'
    ids = []
    while 1:
        url = url_pattern.format(tag, page)
        content = requests.get(url, headers=headers).text
        if page == 21 or u'找不到与标' in content:
            break
        dom = lxml.html.fromstring(content)
        hrefs = dom.xpath('//td[@class="song_name"]/a[1]/@href')
        for href in hrefs:
            song_id = re.findall('\d+', href)[0]
            ids.append(song_id)
        print url
        page += 1

    result = {
        tag: ids,
    }
    print ids
    return process._cache.post(url, json.dumps(result, ensure_ascii=False), refresh=True)
