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
        try:
            response = requests.get(url, headers=headers)   # 适当减少连接失败的情况
        except:
            time.sleep(10)
            continue
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

def get_fans(content):
    # 获取粉丝数量，注意有的网页格式不规范会导致粉丝数不显示，原先位置被‘粉丝’两个字占用
    dom = lxml.html.fromstring(content)
    fans = dom.xpath('//div[@class="music_counts"]//li[1]//a//text()')[0]
    if fans == u'粉丝' or not fans:
        fans = '0'
    return int(fans)

def get_tags(content):   # 同时适用专辑tag，歌曲tag，歌手tag，虾米音乐人tag！
    dom = lxml.html.fromstring(content)
    tags = dom.xpath('//div[contains(@id, "_tags_block")]/div[@class="content clearfix"]/a/text()')
    # 这个contains可以同时覆盖  artist_tags_block, song_tags_block, album_tags_block三种情况，其内部结构相同
    if not tags:
        tags = dom.xpath('//div[@id="artist_tag"]/div[@class="content clearfix"]/a/text()')  # 针对虾米音乐人的情况
    return tags

def get_artist_share(content):  # 得到歌手分享数
    dom = lxml.html.fromstring(content)
    artist_share = dom.xpath('//li[@class="do_share"]//em//text()')   # 成功匹配后的样式为 ['(123)']  需要从列表中取出再去掉括号
    if artist_share:
        artist_share = int(re.findall('\d+',(artist_share[0]))[0])
    else:
        artist_share = 0
    return artist_share

def get_hot_comment(content):   # 得到热评
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

def get_alias(content):      # 经验证，此方法同时适用专辑别名和歌手别名和歌曲别名
    # 此处返回别名的原始字符，最终别名列的处理在清洗步骤完成
    dom = lxml.html.fromstring(content)
    title_node = dom.xpath('//div[contains(@id, "title")]//span//text()')
    if title_node:
        return title_node[0]
    else:
        return ''


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
    result['musicrid']  = song_id
    result['id']        = song_id
    result['hot_comment']   = get_hot_comment(content)
    result['song_alias']    = get_alias(content)
    result['tags'] = get_tags(content)

    lrc = dom.xpath('//div[@class="lrc_main"]//text()')     # 提取歌词
    result['lrc'] = ''.join(lrc).strip()

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
    return True

def get_published_time(content):
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
    return [published_time, timestamp]


def parse_album(album_id):
    url = 'http://www.xiami.com/album/{}'.format(album_id)
    alubm_page_content = get_content(url)
    if not  alubm_page_content:
        return False
    published_time, timestamp = get_published_time(alubm_page_content)
    album_alias               = get_alias(alubm_page_content)
    album_tags                = get_tags(alubm_page_content)
    result_list = []
    page = 1

    while 1:
        url = 'http://www.xiami.com/album/songs/id/{}/page/{}?&_=1476235381636'.format(album_id, page)
        content = get_content(url)
        album_item = json.loads(content)      # 通过上述url可以直接获得json，为一个列表，每个元素为一首歌曲
        print url
        data = album_item[u'data']
        if not data:
            break       # 正常存在data这个key，但是data里面没有内容，说明到了专辑页末尾，翻页结束
        for song_item in data:
            if song_item[u'singerIds']:
                artist_id = song_item[u'singerIds'][0]
            else:
                artist_id = song_item[u'artistId']
            artist_page_url = 'http://www.xiami.com/artist/{}'.format(artist_id)
            artist_page_content = get_content(artist_page_url)
            if not artist_page_content:
                continue

            fans = get_fans(artist_page_content)
            artist_share = get_artist_share(artist_page_content)
            artist_tags  = get_tags(artist_page_content)
            artist_alias = get_alias(artist_page_content)
            result = {                      # 先收集json包含的数据，其它网页内容在parse_song_detail里处理
                'hotness'               : song_item[u'width'],
                'artistid'              : artist_id,
                'singer_ids'            : song_item[u'singerIds'],
                'fans'                  : fans,
                'artist_share'          : artist_share,
                'artist_alias'          : artist_alias,
                'pic'                   : urlparse.urljoin('http://img.xiami.net/i', song_item[u'album_logo']),
                'published_timestamp'   : timestamp,
                'published_time'        : published_time,
                'plays'                 : song_item[u'plays'],
                'pay'                   : song_item[u'needpay'],
                'songName'              : song_item[u'name'],
                'name'                  : song_item[u'name'],
                'artist'                : song_item[u'singers'],
                'album'                 : song_item[u'album_name'],
                'albumid'               : song_item[u'albumId'],
                'song_share'            : song_item[u'recommends'],
                'songOpt'               : song_item[u'songOpt'],
                'raw_api_json'          : song_item,                  # 一次性拿下所有数据，避免以后重爬
                'artist_tags'           : artist_tags,
                'album_tags'            : album_tags,
                'album_alias'           : album_alias,
            }

            success = parse_song_detail(result, song_item[u'songId'])
            # print json.dumps(result, ensure_ascii=False)
            if not success:
                return False
            elif success == 'demo':  # 是demo，跳过
                continue
            else:                   # 不是demo，加入
                result_list.append(result)
        page += 1
    print result_list
    return process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))
    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'artist_id' : re.compile('\d+'),
            'album_url' : re.compile('http://www.xiami.com/artist/album-(\d+)')   
        })
    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    artist_id = url
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        if label == 'artist_id':  # 负责对专辑列表翻页，将每张专辑加到redis队列里
            page = 1
            while 1:
                url = 'http://www.xiami.com/artist/album-{}?page={}'.format(artist_id, page)
                content = get_content(url)
                if not content:
                    return
                dom = lxml.html.fromstring(content)
                albums = dom.xpath('//div[@class="detail"]//p[@class="name"]//@href')
                if len(albums) == 0:
                    break
                for album_href in albums:
                    album_id = re.findall('\d+', album_href)[0]
                    # 开始分析album
                    album_url = 'http://www.xiami.com/artist/album-{}'.format(album_id)
                    if not check_date_ok(album_id):
                        return True
                    manager.put_urls_enqueue(batch_id, [album_url])
                page += 1
            return True

        elif label == 'album_url': # 负责接收专辑URL，以每个专辑为粒度爬取并储存
            album_id = m.group(1)
            return parse_album(album_id)


def check_date_ok(album_id):            # 唯一增加的
    url = 'http://www.xiami.com/album/{}'.format(album_id)
    alubm_page_content = get_content(url)
    if not  alubm_page_content:
        return False
    published_time, published_timestamp = get_published_time(alubm_page_content)
    now = datetime.datetime.utcnow()

    newest_song_date       = time.localtime(published_timestamp)
    days_ago = datetime.date.today() - datetime.timedelta(days=3)
    days_ago_zero = days_ago.timetuple()
    print newest_song_date
    print days_ago_zero
    return newest_song_date >= days_ago_zero

if __name__ == '__main__':
    print check_date_ok('2102642021')
