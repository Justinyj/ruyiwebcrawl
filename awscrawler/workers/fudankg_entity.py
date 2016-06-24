#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
from datetime import datetime

from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_next_batch_id'):
        setattr(process, '_next_batch_id', json.load(open('../config_prefetch/config_fudankg.json'))['batch_ids']['avp'])

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

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    urls = []
    avpair_api = 'http://kw.fudan.edu.cn/cndbpedia/api/entityAVP?entity={}'
    for entity in json.loads(content)[u'entity']:
        urls.append( avpair_api.format(urllib.quote(entity)) )

    manager.put_urls_enqueue(process._next_batch_id, urls)

    return True
