#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
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

from settings import CACHE_SERVER
from invoker.search_zhidao import THE_CONFIG


def process(url, batch_id, parameter, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        setattr(process, '_downloader', DownloadWrapper(CACHE_SERVER, THE_CONFIG['crawl_http_headers']))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        encoding=THE_CONFIG['crawl_result_content_encoding'],
        refresh=THE_CONFIG['crawl_refresh'])

    if content is False:
        return False

    return True
