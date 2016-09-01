#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
import re
import urlparse
import lxml.html
from datetime import datetime
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    # 药材的详情页涉及2个部分：价格历史history和边栏sidebar，以下的ytw/second/是价格历史的url，返回一个大的json；
    # 所以在最后处理的时候还要额外向另一个url发送一次请求，以获得边栏信息,由于要储存到同一个result.json中，因此不再放入队列，而是直接在process里完成
    
    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info('process {}'.format(url))
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_regs'):
        setattr(process, '_regs', {
            'list_view': re.compile('http://www.yt1998.com/price/nowDayPriceQ\!getPriceList.do\?pageIndex=(\d+)&pageSize=(\d+)'),
            'detail_view': re.compile('http://www.yt1998.com/ytw/second/priceInMarket/getPriceHistory.jsp\?ycnam=(.*)&guige=(.*)&chandi=(.*)&market=(.*)')
        })

    if not hasattr(process, '_sellerMarket_list'):
        setattr(process, '_sellerMarket_list', ['', u'亳州市场', u'安国市场', u'玉林市场',u'成都市场'])

    # http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?pageIndex=0&pageSize=500
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        get_logger(batch_id, today_str, '/opt/service/log/').info('label : {}'.format(label))
        if label == 'list_view':
            get_logger(batch_id, today_str, '/opt/service/log/').info(label)
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)
            get_logger(batch_id, today_str, '/opt/service/log/').info('download ok')
            get_logger(batch_id, today_str, '/opt/service/log/').info(len(content))
            list_item = json.loads(content)
            urls = []
            for detail_item in list_item[u'data']:
                detail_url_pattern = 'http://www.yt1998.com/ytw/second/priceInMarket/getPriceHistory.jsp?ycnam={}&guige={}&chandi={}&market={}'
                ycnam = str(detail_item[u'ycnam'])
                chandi = str(detail_item[u'chandi'])
                market = str(detail_item[u'market'])
                guige = str(detail_item[u'guige'])
                detail_url = detail_url_pattern.format(urllib.quote(ycnam), urllib.quote(guige), urllib.quote(chandi), urllib.quote(market))
                urls.append(detail_url)
            get_logger(batch_id, today_str, '/opt/service/log/').info('len urls')
            get_logger(batch_id, today_str, '/opt/service/log/').info(len(urls))
            manager.put_urls_enqueue(batch_id, urls)

            total_num = int(list_item[u'total'])
            pageIndex = int(m.group(1))
            pageSize = int(m.group(2))
            if pageIndex == 0:
                print(total_num // pageSize)
                for index in range(1, total_num // pageSize + 1):
                    get_logger(batch_id, today_str, '/opt/service/log/').info('iiiiiindex')
                    get_logger(batch_id, today_str, '/opt/service/log/').info(index)
                    list_pattern = 'http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?pageIndex={}&pageSize={}'
                    list_url    = list_pattern.format(index, pageSize)
                    manager.put_urls_enqueue(batch_id, [list_url])
            return True
        elif label == 'detail_view':
            get_logger(batch_id, today_str, '/opt/service/log/').info(label)
            ycnam = urllib.unquote(m.group(1))
            guige = urllib.unquote(m.group(2))
            chandi = urllib.unquote(m.group(3))
            market = urllib.unquote(m.group(4))
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)
            get_logger(batch_id, today_str, '/opt/service/log/').info(len(content))
            history_item = json.loads(content)
            get_logger(batch_id, today_str, '/opt/service/log/').info('downloaded')
            price_history = {}
            for raw_daily_data in history_item[u'DayPriceData']:
                date = raw_daily_data[u'Date_time']
                price = raw_daily_data[u'DayCapilization']
                price_history[date] = price
            source_url = 'http://www.yt1998.com/priceHistory.html?keywords={}&guige={}&chandi={}&market={}'
            get_logger(batch_id, today_str, '/opt/service/log/').info('source')
            get_logger(batch_id, today_str, '/opt/service/log/').info(len(process._sellerMarket_list))
            result_item ={
                'name' : ycnam,
                'productGrade': guige,
                'productPlaceOfOrigin' : chandi,
                'sellerMarket'  : process._sellerMarket_list[int(market)],
                'price_history' : price_history,
                'source'        : 'http://www.yt1998.com/priceInfo.html',
            }
            print(result_item)
            result_item['access_time'] = datetime.utcnow().isoformat()  # 从上面source的赋值可看出每个item都对应不同的参数
            return process._cache.post(url, json.dumps(result_item, ensure_ascii = False), refresh = True)
