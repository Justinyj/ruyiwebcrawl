#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER
print REGION_NAME
print CACHE_SERVER

def parse_album_detail(result, album_id, album_cache):
    url = 'http://www.xiami.com/album/{}'.format(album_id)
    content = process.get_content(url)
    if not  content:
        return False
    dom = lxml.html.fromstring(content)
    node = dom.xpath('//div[@id="album_info"]//tr')
    published_time = ''
    for tr_label in node:
        text = tr_label.xpath('./td[1]/text()')[0]
        if u'发行时间' in text:
            published_time = tr_label.xpath('./td[2]/text()')[0]
            break
    result['published_time'] = published_time
    if not u'不详' in published_time:
        timestamp = time.mktime(datetime.datetime.strptime(published_time.encode('utf-8'), '%Y年%m月%d日').timetuple())
    else:
        timestamp = '0'
    timestamp = int(timestamp)
    result['published_timestamp'] = timestamp
    album_cache[album_id] = [published_time, timestamp]
    return

def parse_song_detail(result, song_id):
    if not hasattr(parse_song_detail, '_album_cache'):
        setattr(parse_song_detail, '_album_cache',{})
    url = 'http://www.xiami.com/song/{}'.format(song_id)
    print url
    content = process.get_content(url)
    if not content:    # 此处认为进入demo歌曲页，因此返回结果404
        return True
    dom = lxml.html.fromstring(content)
    unpublished = dom.xpath('//div[@class="unpublished"]')
    if unpublished:
        print ('unpublished:'+url)
        return True

    need_pay = "data-needpay='1'" in content
    if need_pay:
        result['pay'] = 1
    else:
        result['pay'] = 0
        pass
    # is_demo = dom.xpath('//div[@class="demo-player"]')
    # print is_demo
    # if is_demo:
    #     print 'ddddddemo'
    #     return True

    try:
        song_name = dom.xpath('//div[@id="title"]/h1/text()')[0]
    except:
        return False
    albums_info = dom.xpath('//table[@id="albums_info"]//tr')

    album_name     = albums_info[0].xpath('./td[2]//text()')[0]
    album_href  = albums_info[0].xpath('.//@href')[0]
    album_id = re.findall('\d+', album_href)[0]

    artist_name_list    = albums_info[1].xpath('./td[2]/div/a/text()')

    result['artist']    = u'&'.join(artist_name_list)
    result['album']     = album_name
    result['albumid']   = album_id
    result['songName']  = song_name
    result['musicrid']  = song_id
    result['tags']      = []
    result['id']        = song_id
    result['name']      = song_name
    result['pic']     = dom.xpath('//a[@id="albumCover"]/img/@src')[0]
    raw_tags = dom.xpath('//div[@id="song_tags_block"]/div[@class="content clearfix"]/a/text()')
    raw_tags = list(set(raw_tags))  # 得到标签并去重
    if album_name in raw_tags:
        raw_tags.remove(album_name)
    if song_name in raw_tags:
        raw_tags.remove(song_name)

    for ele in artist_name_list:
        if ele.upper() in raw_tags:
            raw_tags.remove(ele.upper())

    result['tags']= raw_tags
    for artist_name in artist_name_list:
        result['tags'].append(u'AN:{}'.format(artist_name))
    result['tags'].append(u'MN:{}'.format(song_name))
    result['tags'].append(u'BN:{}'.format(album_name))
    lrc = dom.xpath('//div[@class="lrc_main"]//text()')   # 得到封面图片
    result['lrc'] = ''.join(lrc)
    result['similar'] = []

    similar_songs = dom.xpath('//div[@id="relate_song"]//tr')
    if similar_songs:
        for song in similar_songs:
            song_url = song.xpath('./td/p/a//@href')[0]
            result['similar'].append(re.findall('\d+', song_url)[0])

    if not parse_song_detail._album_cache.get(album_id, None):
        parse_album_detail(result, album_id, parse_song_detail._album_cache)
    else:
        result['published_time'], result['published_timestamp'] = parse_song_detail._album_cache[album_id]

    res = json.dumps(result, ensure_ascii = False)
    print res.encode('utf-8')
    # return True
    flag = process._cache.post(url, json.dumps(result, ensure_ascii = False), refresh = True)
    return True

def parse_song_list(artist_id):
    page = 1
    song_list_pattern = 'http://www.xiami.com/artist/top-{}?spm=0.0.0.0.qH9VFH&page={}'
    while 1:
        url = song_list_pattern.format(artist_id, page)
        page += 1
        print url
        content = process.get_content(url)
        if not content:
            return False
        print ('download finished')
        dom = lxml.html.fromstring(content)
        table = dom.xpath('//table[@class="track_list"]')[0]
        songs = table.xpath('./tbody/tr')
        if not songs:
            # 达到尾页
            return True

        for song in songs:
            song_hot_bar = song.xpath('./td[@class="song_hot_bar"]/span/@style')[0]
            hot = re.findall('\d+', str(song_hot_bar))[0]
            result = {}
            result['hotness'] = hot
    
            song_href = song.xpath('./td[@class="song_name"]/a/@href')[0]
            song_id = re.findall('\d+', song_href)[0]
    
            success = parse_song_detail(result, song_id)
            if not success:
                return success

            # print result.get('name', None)
        if len(songs) < 20:
            return True


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):


    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
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
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_reg'):
        setattr(process, '_reg', {
            'detail': re.compile('http://app1.sfda.gov.cn/datasearch/face3/content.jsp\?tableId=25&tableName=TABLE25&tableView=%B9%FA%B2%FA%D2%A9%C6%B7&Id=(\d+)'),
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    def get_content(url):
        time.sleep(gap)
        content = process._downloader.downloader_wrapper(
                    url,
                    batch_id,
                    gap,
                    timeout=timeout,
                    encoding='utf-8',
                    refresh=True)
        return content

    if not hasattr(process, 'get_content'):
        setattr(process, 'get_content', get_content)
   
    artist_id = url
    artist_id = '2099990460'
    parse_song_list(artist_id)
    return True

if __name__ == '__main__':
    tt = CachePeriod('tett', CACHE_SERVER)
    tt.post('test.com','{"abc":"123"}',refresh =True)