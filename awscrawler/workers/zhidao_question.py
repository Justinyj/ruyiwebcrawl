#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
from __future__ import print_function, division
import re
import base64
import json

from invoker.zhidao_constant import BATCH_ID
from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import DownloadWrapper
from parsers.zhidao_parser import parse_q_time, parse_q_content, parse_answer_ids, generate_question_json

from settings import REGION_NAME


def get_answer_url(q_id, r_id):
    return ('http://zhidao.baidu.com/question/api/mini?qid={}'
            '&rid={}&tag=timeliness'.format(q_id, r_id))


def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        setattr(process, '_downloader', DownloadWrapper('s3', {'Host': 'zhidao.baidu.com'}, REGION_NAME))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CacheS3(BATCH_ID['json'])


    m = re.search(
        'http://zhidao.baidu.com/question/(\d+).html', url)
    if not m:
        return False

    q_id = m.group(1)
    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout = int(timeout)

    content = process._downloader.downloader_wrapper(url, batch_id, gap, timeout=timeout, encoding='gb18030', error_check=True, refresh=True)
    if content is False:
        return False

    q_json = generate_question_json(q_id, content)
    if q_json is None:
        return False
    elif q_json == {}: # question expired in zhidao
        return True

    question_content = json.dumps(q_json)

    success = process._cache.post(url, question_content)
    if success is False:
        return False

    answer_urls = []
    for answer_id in q_json['answer_ids'][:3]:
        answer_urls.append( get_answer_url(q_id, answer_id) )
    manager.put_urls_enqueue(BATCH_ID['answer'], answer_urls)

    return True
