#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from settings import QUEUE_REDIS, RECORD_REDIS, CACHE_REDIS
from settings import REGION_NAME
from rediscluster.redispool import RedisPool
from rediscluster.queues import Queue
from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

import json
import urllib
import re
import urlparse
import time


SITE = 'https://crl.ptopenlab.com:8800'
batch_id = 'fudankg-20160625'
redispool = RedisPool.instance(RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS)

def run():
    queue = Queue(batch_id)
    for field, value in queue.get_failed_fields().iteritems():
        ret = until_true(value)
        if isinstance(ret, list):
            for url in ret:
                ret = until_true(url)


def until_true(url):
    global batch_id
    for i in xrange(100):
        if i == 10:
            print('This url is crawling 10 times', url)
            return False
        ret = process(url, batch_id, None, None)
        if not isinstance(ret, list):
            if not ret:
                time.sleep(10)
            else:
                return True
        else:
            return ret


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
    
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        0,
        timeout=10,
        encoding='utf-8')

    if content == '':
        return False

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

            return urls
        else:
            data = json.dumps({entity: json.loads(content)})
            return process._cache.post(url, data)

run()

