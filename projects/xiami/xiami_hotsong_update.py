#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import time
import requests
import re
import json
import os
import redis
import lxml.html


redis_id_keyname = 'ruyi-action-xiami-hotmusic'
HASH_KEY = 'ruyi-action-xiami-hotmusic-result'
def slack(msg):
    data = { "text": 'message from ruyi xiami hotmusic update\n{}'.format(msg) }
    print msg
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))


def insert_record_into_redis(record):
    # 更改储存方式为hash
    key = HASH_KEY
    song_id = record['id']
    redis_client.hset(HASH_KEY,song_id, json.dumps(record, ensure_ascii=False))
    insert_id_succees     = redis_client.sadd(redis_id_keyname, song_id)

def get_hot_song():
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.xiami.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    url = 'http://www.xiami.com/chart/data?c=101&type=0&page={}&limit=50&_=1475136767948'
    page = 1
    success = 0
    failed = 0
    records = []

    while 1:
        content =  requests.get(url.format(page), headers=headers).text
        if content == u'empty' or not u'playstatus' in content:
            break
        page += 1
        length = len(re.findall('class="song"', content))
        pic_list = re.findall('src="(.*)"', content)
        song_name_list = re.findall('\">(.*?)?</a></strong>', content)
        song_id_list   = re.findall('song/(\d+)"',content)
        dom = lxml.html.fromstring(content)
        artist_name_list = dom.xpath('//div[@class="info"]/p[2]')
        for index in range(length):
            pic = pic_list[index]
            song_name = song_name_list[index]
            artist_name = ''.join((artist_name_list[index].xpath('.//text()'))).strip()
            print artist_name
            song_id = song_id_list[index]
            record = {
                'id' : song_id,
                'pic' : pic,
                'name' : song_name,
                'artist' : artist_name
            }
            records.append(record)
    delete_old_key()
    for record in records:
        if  insert_record_into_redis(record):
            success += 1
        else:
            failed += 1
    slack('server:ruyi@106.75.13.47\nxiami hot song update  successful : {};failed:{}'.format(success, failed))

def delete_old_key():
    redis_client.delete(redis_id_keyname)  # 每次都清空之前的id,下面是清空之前的key
    redis_client.delete(HASH_KEY)



if __name__ == '__main__':
    redis_client = redis.Redis(host = '10.10.84.141', port=6379, db=0)
    get_hot_song()