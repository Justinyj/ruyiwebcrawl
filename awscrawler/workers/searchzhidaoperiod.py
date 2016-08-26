#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
import re
import urlparse
from datetime import datetime

from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper
from parsers.zhidao_parser import parse_search_json_v0707

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

SITE = 'http://zhidao.baidu.com'

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', re.compile(urlparse.urljoin(SITE, 'search\?word=(.+)')) )


    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)

    today_str = datetime.now().strftime('%Y%m%d')
    word = urllib.unquote( process._regs.match(url).group(1) )

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start download')


    refresh = False
    for _ in range(5):
        try:
            content = process._downloader.downloader_wrapper(url,
                batch_id,
                gap,
                timeout=timeout,
                encoding='gb18030',
                refresh=refresh)

            if content == '':
                return False

            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')


            result = parse_search_json_v0707(content, word)
            break
        except:
            refresh = True


    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start post json')

    return process._cache.post(url, json.dumps(result))
