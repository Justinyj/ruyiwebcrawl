#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# 下架测例：  artist_id   1260
# 付费测例：  artist_id   23549
# 无专辑测例：artist_id 73352507
# 主页跳转： artist_id 7194 、1718627433    这类音乐人为在虾米上有账号的音乐人
# 终极BUG：613269197
# 主页无专辑： 113543

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

from downloader.cacheperiod import CachePeriod

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER


def get_content(url):
    # 有的歌手会有个人主页，会跳转到i.xiami.com,仍要爬取粉丝数
    # 有的歌为demo歌曲，会跳转到i.xiami.com/XXX/demo/xxx ,不爬取
    # todo :统一返回类型，更换手段处理demo情况
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
    for _ in range(3):
        time.sleep(1)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            break
        elif response.url != url:
            url = response.url
            headers = {}                  # 对于i.xiami.com 网页，不需要headers
            if 'demo' in url:
                return '' 
    else:
        return False

    return response.text

def parse_album_detail(album_id):
    # 解析专辑页面，主要是为了得到时间，再转化为相应时间戳
    # 现在是设置成返回二元组，不是一个恰当的选择，返回字典更合适
    if not hasattr(parse_album_detail, '_album_cache'):
        setattr(parse_album_detail, '_album_cache',{})

    result = parse_album_detail._album_cache.get(album_id, None)
    if result:                  #  已缓存
        return result
    elif not album_id:          # 不存在专辑页
        parse_album_detail._album_cache[album_id] = ['', 0]
        return ['', 0]
    else:                       # 未缓存，且存在专辑页
        url = 'http://www.xiami.com/album/{}'.format(album_id)
        content = get_content(url)
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

        if  u'不详' in published_time:
            timestamp = 0
        else:
            timestamp = int(time.mktime(datetime.datetime.strptime(published_time.encode('utf-8'), '%Y年%m月%d日').timetuple()))
        parse_album_detail._album_cache[album_id] = [published_time, timestamp]
        return [published_time, timestamp]

def get_hot_comment(content):
    dom = lxml.html.fromstring(content)
    hot_comment_node = dom.xpath('//div[@class="hotComment"]')
    if not hot_comment_node:
        return []
    else:
        comments = hot_comment_node[0].xpath('.//div[@class="brief"]//div')
        result = []
        for comment in comments:                # 之所以不在上面完成对text的提取是因为多行评论的时候会处在不同的标签内
            text = ''.join(comment.xpath('.//text()'))
            result.append(text.strip())
        return result

def parse_song_detail(result, song_id):
    # 需要得到：歌曲标签，歌词，相似歌曲，发行日期（从专辑页面中获取，注意要缓存，否则每首歌都重复访问一次专辑页面）
    url = 'http://www.xiami.com/song/{}'.format(song_id)
    content = get_content(url)
    if content == '':      
        return 'demo'
    elif content == False:
        return False
    dom = lxml.html.fromstring(content)

    result['unpublished'] = 1 if dom.xpath('//div[@class="unpublished"]') else 0
    result['pay'] = 1 if "data-needpay='1'" in content else 0

    song_name = dom.xpath('//div[@id="title"]/h1/text()')[0]

    albums_info = dom.xpath('//table[@id="albums_info"]//tr')
    try:                        # 有150位左右的歌手有部分歌曲不存在专辑
        album_name     = albums_info[0].xpath('./td[2]//text()')[0]
        album_href  = albums_info[0].xpath('.//@href')[0]
        album_id = re.findall('\d+', album_href)[0]
    except:
        album_name = ''
        album_id   = ''

    artist_name_list    = albums_info[1].xpath('./td[2]/div/a/text()')
    result['artist']    = u'&'.join(artist_name_list)
    result['album']     = album_name
    result['albumid']   = album_id
    result['songName']  = song_name
    result['musicrid']  = song_id
    result['tags']      = []
    result['id']        = song_id
    result['name']      = song_name
    result['pic']       = dom.xpath('//a[@id="albumCover"]/img/@src')[0]  # 得到封面图片
    result['hot_comment']   = get_hot_comment(content)
    raw_tags = dom.xpath('//div[@id="song_tags_block"]/div[@class="content clearfix"]/a/text()')
    raw_tags = list(set(raw_tags))  # 得到标签并去重

    if album_name and album_name in raw_tags:   
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

    lrc = dom.xpath('//div[@class="lrc_main"]//text()')     # 提取歌词
    result['lrc'] = ''.join(lrc).strip()


    song_share = dom.xpath('//div[@class="music_counts"]//li[1]//text()')
    if song_share:
        song_share = int(song_share[0])
    else:
        song_share = 0
    result['song_share'] = song_share

    comment_cnt = dom.xpath('//div[@class="music_counts"]//li[2]//text()')
    try:
        comment_cnt = int(comment_cnt[0])
    except:
        comment_cnt = 0

    result['comment_cnt'] = comment_cnt

    result['similar'] = []
    similar_songs = dom.xpath('//div[@id="relate_song"]//tr')
    if similar_songs:
        for song in similar_songs:
            song_url = song.xpath('./td/p/a//@href')[0]
            result['similar'].append(re.findall('\d+', song_url)[0])

    result['published_time'], result['published_timestamp'] = parse_album_detail(album_id)
    print json.dumps(result, ensure_ascii=False).encode('utf-8')
    return True


def get_hotness(dom):
    song_hot_bar = dom.xpath('./td[@class="song_hot_bar"]/span/@style')[0]
    return re.findall('\d+', str(song_hot_bar))[0]


def get_fans(content):
    # 获取粉丝数量，注意有的网页格式不规范会导致粉丝数不显示，原先位置被‘粉丝’两个字占用
    dom = lxml.html.fromstring(content)
    fans = dom.xpath('//div[@class="music_counts"]//li[1]//a//text()')[0]
    if fans == u'粉丝' or not fans:
        fans = '0'
    return int(fans)

def get_artist_share(content):
    dom = lxml.html.fromstring(content)
    artist_share = dom.xpath('//li[@class="do_share"]//em//text()')   # 成功匹配后的样式为 ['(123)']  需要从列表中取出再去掉括号
    if artist_share:
        artist_share = int(re.findall('\d+',(artist_share[0]))[0])
    else:
        artist_share = 0
    return artist_share

def get_artist_alias(content):
    # 此处返回别名的原始字符，最终别名列的处理在清洗步骤完成
    dom = lxml.html.fromstring(content)
    title_node = dom.xpath('//div[contains(@id, "title")]//span//text()')
    if title_node:
        return title_node[0]
    else:
        return ''



def parse_song_list(artist_id):
    # 页面介绍：每个歌手的歌曲列表 such as :http://www.xiami.com/artist/top-1260
    # 函数目的：预先得到粉丝数和热度这种歌曲，同时进行翻页， 每首歌的详细信息在parse_song_detail中处理
    # 获取粉丝数量，注意有的网页不规范会导致‘粉丝’两个字占用原来应该是粉丝数的位置
    artist_page_url = 'http://www.xiami.com/artist/{}'.format(artist_id)
    artist_page_content = get_content(artist_page_url)
    if not artist_page_content:
        return False
    fans = get_fans(artist_page_content)
    artist_share = get_artist_share(artist_page_content)
    alias = get_artist_alias(artist_page_content)

    result_list = []
    page = 1
    song_list_pattern = 'http://www.xiami.com/artist/top-{}?spm=0.0.0.0.qH9VFH&page={}'    
    while 1:
        url = song_list_pattern.format(artist_id, page)
        page += 1
        content = get_content(url)
        if not content:
            return False

        dom = lxml.html.fromstring(content)
        table = dom.xpath('//table[@class="track_list"]')[0]

        songs = table.xpath('.//tr')
        if not songs:           # 达到尾页
            return result_list

        for song in songs:
            result = {
                'hotness' : get_hotness(song),
                'artistid': artist_id,
                'fans'    : fans,
                'artist_share':artist_share,
                'artist_alias'       : alias,
            }
            # print json.dumps(result, ensure_ascii=False).encode('utf-8')
            song_href = song.xpath('./td[@class="song_name"]/a/@href')[0]
            song_id = re.findall('\d+', song_href)[0]

            success = parse_song_detail(result, song_id)
            if not success:
                return False
            elif success == 'demo':  # 是demo，跳过
                continue
            else:  # 不是demo，加入
                result_list.append(result)

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))
    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)
    artist_id = url
    result_list = parse_song_list(artist_id)
    if result_list == False:       # 因为也可能是空列表，所以采取这种判断方式
        return False
    else:
        flag =  process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)
        return True
