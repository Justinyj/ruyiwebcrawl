#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
import sys
import re
import json
import base64
import traceback
import requests
import time

import lxml.html
import urlparse

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from downloader.downloader_wrapper import Downloader

from settings import REGION_NAME

from crawlerlog.cachelog import get_logger
from datetime import datetime

def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        encoding='gb18030')
    get_logger(batch_id, today_str, '/opt/service/log/').info('stop download')

    if kwargs and kwargs.get("debug"):
        print(len(content), "\n", content[:1000])

    if content is False:
        return False

    content_urls = []

    get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing')
    tree = lxml.html.fromstring(content)
    urls = tree.xpath('//td[@class="title"]/a/@href')
    if urls == []:
        get_logger(batch_id, today_str, '/opt/service/log/').info('start download2')
        content = process._downloader.downloader_wrapper(url,
            batch_id,
            gap,
            timeout=timeout,
            encoding='gb18030',
            refresh=True)
        get_logger(batch_id, today_str, '/opt/service/log/').info('stop download2')
        if content is False:
            return False
        tree = lxml.html.fromstring(content)
        urls = tree.xpath('//td[@class="title"]/a/@href')

    for url in urls:
        content_urls.append( urlparse.urljoin('http://data.eastmoney.com/', url) )
    get_logger(batch_id, today_str, '/opt/service/log/').info('stop parsing')

    get_logger(batch_id, today_str, '/opt/service/log/').info('start put content')
    manager.put_urls_enqueue('dongcaigonggao-content-20160620', content_urls)
    get_logger(batch_id, today_str, '/opt/service/log/').info('stop put content')

    return True
