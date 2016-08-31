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

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

SITE = 'http://www.qichacha.com'

def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        cookie = kwargs.get('cookie', None)
        if cookie:
            headers.update({'Cookie': cookie})
        setattr(process, '_downloader', DownloadWrapper('s3', headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'search': re.compile(urlparse.urljoin(SITE, 'search\?key=(.+?)&index=(\d+)')),
            'detail': re.compile(urlparse.urljoin(SITE, 'firm_(\w+?).shtml')),
            'invest': re.compile(urlparse.urljoin(SITE, 'company_getinfos\?unique=(\w+?)&companyname=(.+?)(?:&p=(\d+))?&tab=touzi(?:&box=touzi)?')),
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    today_str = datetime.now().strftime('%Y%m%d')

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start download')

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        method,
        timeout=timeout,
        encoding='utf-8')

    if content == '':
        return False

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue

