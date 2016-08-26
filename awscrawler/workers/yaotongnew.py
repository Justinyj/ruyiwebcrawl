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

# from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
# from settings import CACHE_SERVER

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
            'list_view': re.compile('http://www.yt1998.com/price/nowDayPriceQ!getPriceList.do?pageIndex=250&pageSize=20')

        })

    # if not hasattr(process, '_cache'):
    #     head, tail = batch_id.split('-')
    #     setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        get_logger(batch_id, today_str, '/opt/service/log/').info('label : {}'.format(label))

            # return process._cache.post(url, json.dumps(result_item, ensure_ascii = False), refresh = True)
