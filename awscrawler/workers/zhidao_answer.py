#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
from __future__ import print_function, division

import os
import sys
import logging
import re
import json
import base64
import traceback
import logging
import requests
from invoker.zhidao import BATCH_ID
from zhidao_tools import get_content
HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1'
}

def generate_answer_js(ans_content):
    try:
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
    except:
        traceback.print_exc()
        print('获取答案出错')
        print('q_id:', q_id)
        print('answer_id', answer_id)
        logging.debug('获取答案出错,q_id:{},answer_id:{}'.format(q_id, answer_id))
        return None


def worker(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')
    content = get_zhidao_content(url, method, gap, HEADER, BATCH_ID['answer'])
    if content is None:
        return False
    ans_content = generate_answer_js(content)
    if ans_content is None:
        return False
    m = Cache(BATCH_ID['json'])
    flag = m.post(url, ans_content)
