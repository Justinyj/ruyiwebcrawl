#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
import json
import urllib
import re
from datetime import datetime

from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CacheS3(batch_id.split('-', 1)[0] + '-json'))

    if not hasattr(process, '_regentity'):
        setattr(process, '_regentity', re.compile('http://kw.fudan.edu.cn/cndbpedia/api/entity\?mention=(.+)'))
    if not hasattr(process, '_regavp'):
        setattr(process, '_regavp', re.compile('http://kw.fudan.edu.cn/cndbpedia/api/entityAVP\?entity=(.+)'))


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

    m = process._regentity.match(url)
    if m:
        entity = urllib.unquote(m.group(1))
        urls = []
        avpair_api = 'http://kw.fudan.edu.cn/cndbpedia/api/entityAVP?entity={}'
        for ent in json.loads(content)[u'entity']:
            if isinstance(ent, unicode):
                ent = ent.encode('utf-8')
            urls.append( avpair_api.format(urllib.quote(ent)) )

        manager.put_urls_enqueue(batch_id, urls)
        return True

    else:
        m = process._regavp.match(url)
        if m:
            entity = urllib.unquote(m.group(1))
            eavp = json.dumps({entity: json.loads(content).values()[0]})

            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('start post json')

            return process._cache.post(url, eavp)

