#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
import re
import urlparse
from datetime import datetime

from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME

SITE = 'http://zhidao.baidu.com'


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CacheS3(head + '-json-' + tail))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', re.compile(urlparse.urljoin(SITE, 'search\?word=(.+)')) )


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    today_str = datetime.now().strftime('%Y%m%d')

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start download')

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        encoding='utf-8')

    if content == '':
        return False

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')
