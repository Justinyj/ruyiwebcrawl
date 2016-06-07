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
from tools import get_content
HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1'
}
HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1'
}


def parse_q_id(content):
    q_id = re.search(
        'rel="canonical" href="http://zhidao.baidu.com/question/(\d+).html"', content)
    if q_id is not None:
        q_id = q_id.group(1)
        return q_id
    return None


def parse_title(content):
    m = re.search('<title>(.*)</title>', content)
    if m is not None:
        title = m.group(1)
        if ("_百度知道") not in title:
            print('未找到title或者页面不存在:')
            return None
        title = re.sub("_百度知道", "", title)
        return title
    return None


def parse_q_time(content):
    m = re.search(
        '<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is not None:
        q_time = m.group(1)
        return q_time
    return None


def parse_q_content(content):
    q_content = ''
    m = re.search('accuse="qContent">(.*)</pre>', content)
    n = re.search('accuse="qSupply">(.*)</pre>', content)
    if m is not None:
        q_content = m.group(1)
        q_content = re.sub("<.*?>", "\n", q_content)
        q_content = q_content.strip()
        if n is not None:
            supply = n.group(1)
            q_content = q_content + supply
        return q_content
    return None


def parse_answer_ids(content):
    result = map(int, re.findall('id="answer-(\d+)', content))[:3]
    return result


def get_question_js(content):
    q_title = parse_title(content)
    if q_title is None:
        print('未找到title或者页面不存在')
        logging.debug('未找到title或者页面不存在,q_id:{}'.format(q_id))
        # counter['invalid page']+=1
        return None
    q_id = parse_q_id(content)
    q_content = parse_q_content(content)
    q_time = parse_q_time(content)
    answer_ids = parse_answer_ids(content)
    if len(answer_ids) == 0:
        print('该问题没有回答，q_id:{}'.format(q_id))
        logging.debug('该问题没有回答，q_id:{}'.format(q_id))
    item = {
        'question_id': q_id,
        'question_title': q_title,
        'question_detail': q_content,
        'question_time': q_time,
        'answers': answer_ids,
    }
    question_content = json.dumps(item)
    return question_content


def worker(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')
    content = get_content(url, method, gap, HEADER, BATCH_ID['question'])
    get_question_js(content)

    m = Cache(BATCH_ID['json'])
    m.post(url, question_content)
    # answer_list=parse_answer_ids(content)
    # answer_url_list=get_answer_url(q_id,ans_id)
