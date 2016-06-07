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
from invoker.zhidao import BATCH_ID,HEADER
from zhidao_tools import get_zhidao_content


def parse_q_id(content):
    q_id = re.search(
        'rel="canonical" href="http://zhidao.baidu.com/question/(\d+).html"', content)
    if q_id:
        q_id = q_id.group(1)
        return q_id
    return None


def parse_title(content):
    m = re.search('<title>(.*)</title>', content)
    if m:
        title = m.group(1)
        if ("_百度知道") not in title:
            if ("百度知道-信息提示") == title:
                return None
            return None
        title = re.sub("_百度知道", "", title)
        return title
    return None


def parse_q_time(content):
    m = re.search(
        '<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is None:
        return None
    q_time = m.group(1)
    return q_time


def parse_q_content(content):
    q_content = ''
    m = re.search('accuse="qContent">(.*)</pre>', content)
    n = re.search('accuse="qSupply">(.*)</pre>', content)
    if m:
        q_content = m.group(1)
        q_content = re.sub("<.*?>", "\n", q_content)
        q_content = q_content.strip()
        if n:
            supply = n.group(1)
            q_content = q_content + supply
        return q_content
    return None


def parse_answer_ids(content):
    result = map(int, re.findall('id="answer-(\d+)', content))
    return result


def generate_question_js(content):
    q_title = parse_title(content)
    if q_title is None:
        # print('未找到title或者页面不存在')
        return None
    q_id = parse_q_id(content)
    q_content = parse_q_content(content)
    q_time = parse_q_time(content)
    answer_ids = parse_answer_ids(content)
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
    content = get_zhidao_content(
        url, method, gap, HEADER, BATCH_ID['question'])
    if content is u'':
        return False

    question_content = generate_question_js(content)
    if question_contentis is None:
        return False
    m = Cache(BATCH_ID['json'])
    flag = m.post(url, question_content)
    if not flag:
        time.sleep(10)
        flag=m.post(url, ans_content)
    return flag
    # return flag['success']
    # answer_list=parse_answer_ids(content)
    # answer_url_list=get_answer_url(q_id,ans_id)
