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
import pytz
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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

def check_date_ok(url):                                  # 药通网的新闻每天北京时间10~12点更新，爬虫可以设成北京时间13~14点爬取，
    now = datetime.datetime.utcnow()
    content = requests.get(url).text
    item = json.loads(content)
    dtm  = item['data'][0]['dtm']                       # 判断某页最新的时间是否过旧
    news_date = time.strptime(dtm,'%Y-%m-%d %H:%M:%S')    

    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    
    yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_zero = yesterday_date.timetuple()
    print yesterday_date
    print yesterday_zero
    return news_date > yesterday_zero

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    print (url)
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
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        if label == 'column_id':
            query_url = 'http://www.yt1998.com/ytw/second/marketMgr/query.jsp'
            column_id = url
            page_size = 10
            data = {
                'lmid':column_id,                   # 栏目id，lm是栏目的首字母! 9代表产地信息，1代表品种分析，3代表天天行情
                # 'scid':'1',                       # 对于天天行情，存在scid=市场id，但是尝试不传递这个参数，就会返回所有市场的新闻。且在返回值内依然可以找到市场字段，不会丢失信息。
                'pageIndex' : '0',
                'pageSize'  : page_size,
                'times'     : '1',                  # 非必要参数
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
            total = int(news_info[u'total'])        # 得出新闻总数，以此生成子任务
            url_pattern = 'http://www.yt1998.com/ytw/second/marketMgr/query.jsp?lmid={}&times=1&pageIndex={}&pageSize={}'
            urls = []
            for index in range(0, total / page_size + 1):
                url = url_pattern.format(column_id, index, page_size)
                if not check_date_ok(url):
                    break
                urls.append(url)
            manager.put_urls_enqueue(batch_id, urls)

        elif label == 'pages_view':
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
                else:                                       # 其它栏目进行正文爬取
                    result['news_content'] = get_news_content(result['news_url'], batch_id, gap, timeout)
                result_list.append(result)
            return process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)
