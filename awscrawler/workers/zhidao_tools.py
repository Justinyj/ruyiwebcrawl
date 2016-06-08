#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
from __future__ import print_function, division

import os
import sys
import json
import requests

from downloader.downloader import Downloader
from invoker.zhidao import BATCH_ID


DATA_PATH = os.path.abspath(os.path.dirname(
    __file__))
VERSION = "201606"

question_template = 'http://zhidao.baidu.com/question/{}.html'
ANSWER_URL = 'http://zhidao.baidu.com/question/api/mini?qid={}&rid={}&tag=timeliness'


def get_answer_url(q_id, r_id):
    return ANSWER_URL.format(q_id, r_id)


def get_zhidao_content(url, method, gap, header, batch_id):
    if not hasattr(get_zhidao_content, '_batches'):
        setattr(get_zhidao_content, '_batches', {})

    ret = get_zhidao_content._batches.get(batch_id)
    if ret is None:
        downloader = Downloader(request=True, gap=gap, batch_id=batch_id)
        downloader.login()
        get_zhidao_content._batches[batch_id] = downloader

    if header:
        get_zhidao_content._batches[batch_id].update_header(header)

    return get_zhidao_content._batches[batch_id].requests_with_cache(
            url, 'get', encode='gb18030', refresh=False)
