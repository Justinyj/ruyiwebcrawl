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

from invoker.zhidao_constant import BATCH_ID
from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from parsers.zhidao_parser import generate_answer_json

from settings import CACHE_SERVER


def process(url, batch_id, parameter, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        setattr(process, '_downloader', DownloadWrapper(CACHE_SERVER, {'Host': 'zhidao.baidu.com'}))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', Cache(BATCH_ID['json'], CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout = int(timeout)

    content = process._downloader.downloader_wrapper(url, batch_id, gap, timeout=timeout, encoding='gb18030', refresh=True)
    if content is False:
        return False

    if content == u'""':
        raise Exception('question with other relatated answer')

    a_json = generate_answer_json(content)
    ans_content = json.dumps(a_json)
    return process._cache.post(url, ans_content)
