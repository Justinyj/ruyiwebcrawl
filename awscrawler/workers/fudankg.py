#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
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

#SITE = 'http://kw.fudan.edu.cn'
SITE = 'https://crl.ptopenlab.com:8800'

def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CacheS3(head + '-json-' + tail))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'entity': re.compile(urlparse.urljoin(SITE, 'cndbpedia/api/entity\?mention=(.+)')),
            'avp': re.compile(urlparse.urljoin(SITE, 'cndbpedia/api/entityAVP\?entity=(.+)')),
            'info': re.compile(urlparse.urljoin(SITE, 'cndbpedia/api/entityInformation\?entity=(.+)')),
            'tags': re.compile(urlparse.urljoin(SITE, 'cndbpedia/api/entityTag\?entity=(.+)')),
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

        entity = urllib.unquote(m.group(1))
        if label == 'entity':
            urls = []
            avpair_api = urlparse.urljoin(SITE, 'cndbpedia/api/entityAVP?entity={}')
            info_api = urlparse.urljoin(SITE, 'cndbpedia/api/entityInformation?entity={}')
            tags_api = urlparse.urljoin(SITE, 'cndbpedia/api/entityTag?entity={}')
            js = json.loads(content)
            for ent in js[u'entity']:
                if isinstance(ent, unicode):
                    ent = ent.encode('utf-8')
                ent = urllib.quote(ent)
                urls.append( avpair_api.format(ent) )
                urls.append( info_api.format(ent) )
                urls.append( tags_api.format(ent) )

            manager.put_urls_enqueue(batch_id, urls)

            return True
        else:
            data = json.dumps({entity: json.loads(content)})

            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('start post {} json'.format(label))

            return process._cache.post(url, data)

