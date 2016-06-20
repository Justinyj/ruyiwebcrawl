#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# common crawler, only do prefetch, no parsing

from __future__ import print_function, division

import os
import sys
import re
import json
import base64
import traceback
import requests
import time

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from downloader.downloader_wrapper import Downloader

from settings import CACHE_SERVER


def process(url, batch_id, parameter, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        #{'Host': 'zhidao.baidu.com'}
        headers = {"Host": domain_name}
        setattr(process, '_downloader', DownloadWrapper(CACHE_SERVER, headers))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout)

    if kwargs and kwargs.get("debug"):
        print( len(content), "\n", content[:1000])

    if content is False:
        return False

    return True
