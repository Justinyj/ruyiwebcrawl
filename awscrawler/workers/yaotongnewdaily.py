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

    # http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?pageIndex=0&pageSize=20
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
            list_item = json.loads(content)
            for detail_item in list_item[u'data']:
                detail_item[u'access_time'] = datetime.utcnow().isoformat()

            total_num = int(list_item[u'total'])
            pageIndex = int(m.group(1))
            pageSize = int(m.group(2))
            if pageIndex == 0:
                for index in range(1, total_num // pageSize + 1):
                    get_logger(batch_id, today_str, '/opt/service/log/').info('index:')
                    get_logger(batch_id, today_str, '/opt/service/log/').info(index)
                    list_pattern = 'http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?pageIndex={}&pageSize={}'
                    list_url    = list_pattern.format(index, pageSize)
                    manager.put_urls_enqueue(batch_id, [list_url])

            return process._cache.post(url, json.dumps(list_item, ensure_ascii = False), refresh = True)
