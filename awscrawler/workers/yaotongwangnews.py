#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from datetime import datetime

import json
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
from settings import REGION_NAME, CACHE_SERVER



def get_news_content(url, batch_id, gap, timeout):
    content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            method='get',
            timeout = timeout,
            encoding = 'utf-8',
            refresh = True)
    dom = lxml.html.fromstring(content)
    news_content = dom.xpath('//div[contains(@style,"text-indent")]//text()')
    return '\n'.join(news_content).strip()

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))

    if not hasattr(process,'_regs'):
        setattr(process, '_regs', {
            'column_id': re.compile('(\d+)'),
            'pages_view': re.compile('http://www.yt1998.com/ytw/second/marketMgr/query.jsp\?lmid=(\d+?)&(.*)')
        })
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)
    print url
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        print label
        if label == 'column_id':
            query_url = 'http://www.yt1998.com/ytw/second/marketMgr/query.jsp'
            column_id = url
            page_size = 10
            data = {
                'lmid':column_id,                   # 栏目id，lm是栏目的首字母! 9代表产地信息，1代表品种分析，3代表天天行情
                # 'scid':'1',                       # 对于天天行情，存在scid=市场id，但是尝试不传递这个参数，就会返回所有市场的新闻。且在返回值内依然可以找到市场字段，不会丢失信息。
                'pageIndex' : '0',
                'pageSize'  : page_size,
                'times'     : '1',                        # 非必要参数
            }
            content = process._downloader.downloader_wrapper(
                    query_url,
                    batch_id,
                    gap,
                    method='post',
                    data=data,
                    timeout = timeout,
                    encoding = 'utf-8',
                    refresh = True)
            news_info = json.loads(content)
            total = int(news_info[u'total'])            # 得出新闻总数，以此生成子任务
            url_pattern = 'http://www.yt1998.com/ytw/second/marketMgr/query.jsp?lmid={}&times=1&pageIndex={}&pageSize={}'
            urls = []
            for index in range(0, total / page_size + 1):
                url = url_pattern.format(column_id, index, page_size)
                urls.append(url)
            print total
            print url
            manager.put_urls_enqueue(batch_id, urls)
        elif label == 'pages_view':
            lmid = int(m.group(1))
            content = process._downloader.downloader_wrapper(
                    url,
                    batch_id,
                    gap,
                    method='get',
                    timeout = timeout,
                    encoding = 'utf-8',
                    refresh = True)
            item = json.loads(content)
            news_data = item[u'data']
            menu_dic = {
                '1' : u'品种分析',
                '3' : u'天天行情',
                '9' : u'产地信息',
            }
            result_list = []
            detail_pattern = 'http://www.yt1998.com/hqMinute--{}.html'
            for news in news_data:
                result = {
                    'news_title'        : news[u'title'],
                    'news_url'          : detail_pattern.format(news[u'acid']),
                    'news_desc'         : news[u'cont'].strip(),
                    'news_date'         : news[u'dtm'],
                    'news_keyword_list' : [news[u'ycnam']],                    # ycname = 药材nam = 药材name 取名逻辑很复杂
                    'access_time'       : datetime.datetime.utcnow().isoformat(),
                    'market'            : news[u'market'],
                }
                result['news_type'] = menu_dic[news[u'lmid']]
                if news[u'lmid'] == '3':                    # 天天行情为快讯，是短新闻，不用再去取正文
                    result['news_content'] = result['news_desc']
                else:
                    result['news_content'] = get_news_content(result['news_url'], batch_id, gap, timeout)
                result_list.append(result)
            print process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)
            return True

if __name__ == '__main__':
    # process('1')
    process('http://www.yt1998.com/ytw/second/marketMgr/query.jsp?lmid=9&times=1&pageIndex=0&pageSize=10')