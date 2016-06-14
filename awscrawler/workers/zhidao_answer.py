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

from invoker.zhidao import BATCH_ID
from downloader.cache import Cache
from .zhidao_tools import zhidao_download, get_answer_url
from .zhidao_parser import generate_answer_json


def process(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')
    gap = int(gap)

    content = zhidao_download(url, BATCH_ID['answer'], gap, error_check=False)
    if content is False:
        return False

    try:
        a_json = generate_answer_json(content)
        ans_content = json.dumps(a_json)
    except:
        return False
    m = Cache(BATCH_ID['json'])
    return m.post(url, ans_content)
