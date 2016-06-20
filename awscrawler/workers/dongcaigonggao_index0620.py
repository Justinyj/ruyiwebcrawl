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

from settings import CACHE_SERVER


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {"Host": domain_name}
        setattr(process, '_downloader', DownloadWrapper(CACHE_SERVER, headers))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        encoding='gb18030')

    if kwargs and kwargs.get("debug"):
        print(len(content), "\n", content[:1000])

    if content is False:
        return False

    content_urls = []
    tree = lxml.html.fromstring(content)
    urls = tree.xpath('//td[@class="title"]/a/@href')
    if urls == []:
        content = process._downloader.downloader_wrapper(url,
            batch_id,
            gap,
            timeout=timeout,
            encoding='gb18030',
            refresh=True)
        if content is False:
            return False
        tree = lxml.html.fromstring(content)
        urls = tree.xpath('//td[@class="title"]/a/@href')

    for url in urls:
        content_urls.append( urlparse.urljoin('http://data.eastmoney.com/', url) )

    manager.put_urls_enqueue('dongcaigonggao-content-20160620', content_urls)

    return True
