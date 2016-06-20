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

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from downloader.downloader_wrapper import Downloader

from settings import CACHE_SERVER


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {"Host": domain_name}
        setattr(process, '_downloader', DownloadWrapper(CACHE_SERVER, headers))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', Cache(batch_id.split('-', 1)[0]+'-json', CACHE_SERVER))

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

    tree = lxml.html.fromstring(content)
    title = tree.xpath('//div[@class="content"]/h4/text()')
    if isinstance(title, list) and len(title) > 0:
        title = title[0]
    else:
        title = None
    public_date = tree.xpath('//div[@class="content"]/h5/text()')
    if isinstance(public_date, list) and len(public_date) > 0:
        public_date = public_date[0]
    else:
        public_date = None
    body = tree.xpath('//div[@class="content"]//pre/text()')
    if isinstance(body, list) and len(body) > 0:
        body = body[0]
    else:
        body = None
    notice_content = json.dumps({'url': url, 'title': title, 'public_date': public_date, 'body': body})

    return process._cache.post(url, notice_content)
