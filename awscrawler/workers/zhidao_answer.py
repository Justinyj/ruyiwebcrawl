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
from invoker.zhidao import BATCH_ID, HEADER
from zhidao_tools import get_zhidao_content, get_answer_url
from downloader.cache import Cache


def generate_answer_json(ans_content):
    content = json.loads(ans_content)
    answer = {
        'question_id': content[u'qid'],
        'answer_id': content[u'id'],
        'isBest': content[u'isBest'],
        'isHighQuality': content[u'isHighQuality'],
        'isExcellent': content[u'isExcellent'],
        'isRecommend': content[u'isRecommend'],
        'isSpecial': content[u'isSpecial'],
        'createTime': content[u'createTime'],
        'recommendCanceled': content[u'recommendCanceled'],
        'content': content[u'content'].encode('utf-8'),
        'valueNum': content[u'valueNum'],
        'valueBadNum': content[u'valueBadNum'],
    }
    return json.dumps(answer)


def process(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')
    gap = int(gap)

    for _ in range(2):
        content = get_zhidao_content(url, method, gap, HEADER, BATCH_ID['answer'], error_check=False)
        if content != u'':
            break
        time.sleep(gap)
    else:
        return False

    ans_content = generate_answer_json(content)
    if ans_content is None:
        return False
    m = Cache(BATCH_ID['json'])
    flag = m.post(url, ans_content)
    if not flag:
        flag = m.post(url, ans_content)
    return flag
