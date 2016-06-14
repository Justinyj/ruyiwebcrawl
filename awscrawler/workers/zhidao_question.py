#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
from __future__ import print_function, division
import re
import base64
import json

from invoker.zhidao import BATCH_ID
from downloader.cache import Cache
from .zhidao_tools import zhidao_download, get_answer_url
from .zhidao_parser import parse_title, parse_q_time, parse_q_content, parse_answer_ids, generate_question_json



def process(url, parameter, manager, *args, **kwargs):
    m = re.search(
        'http://zhidao.baidu.com/question/(\d+).html', url)
    if not m:
        return False

    q_id = m.group(1)
    method, gap, js, data = parameter.split(':')
    gap = int(gap)
    batch_id = BATCH_ID['question']

    content = zhidao_download(url, batch_id, gap, method)
    if content is False:
        return False

    answer_ids = []
    q_json = generate_question_json(q_id, content, answer_ids)
    if q_json is None:
        return False

    question_content = json.dumps(q_json)

    m = Cache(BATCH_ID['json'])
    success = m.post(url, question_content)
    if success is False:
        return False

    answer_urls = []
    for answer_id in answer_ids[:3]:
        answer_urls.append( get_answer_url(q_id, answer_id) )
    manager.put_urls_enqueue(BATCH_ID['answer'], answer_urls)

    return True
