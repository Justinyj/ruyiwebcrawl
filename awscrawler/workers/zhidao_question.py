#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
from __future__ import print_function, division
import time
import os
import sys
import re
import json
import base64
import traceback
import requests
from invoker.zhidao import BATCH_ID, HEADER
from zhidao_tools import get_zhidao_content, get_answer_url
from awscrawler import get_distributed_queue, put_url_enqueue


def parse_q_id(content):
    q_id = re.search(
        'rel="canonical" href="http://zhidao.baidu.com/question/(\d+).html"', content)
    if q_id:
        q_id = q_id.group(1)
        return q_id
    return


def parse_title(content):
    m = re.search('<title>(.*)</title>', content)
    if m:
        title = m.group(1)
        if ("_百度知道") not in title:
            if ("百度知道-信息提示") == title:
                return
            return
        title = re.sub("_百度知道", "", title)
        return title
    return


def parse_q_time(content):
    m = re.search(
        '<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is None:
        return
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
    return


def parse_answer_ids(content):
    result = map(int, re.findall('id="answer-(\d+)', content))
    return result


def generate_question_json(content,rids):
    q_title = parse_title(content)
    if q_title is None:
        # print('未找到title或者页面不存在')
        return
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


def process(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')
    batch_id = BATCH_ID['question']
    content = get_zhidao_content(
        url, method, gap, HEADER, batch_id)
    if content is u'':
        time.sleep(gap)
        content = get_zhidao_content(
            url, method, gap, HEADER, batch_id)
    if content is u'':
        return False
    answer_ids=[]
    question_content = generate_question_json(content,answer_ids)
    if question_contentis is None:
        return False
    m = Cache(BATCH_ID['json'])
    flag = m.post(url, question_content)
    if not flag:
        flag = m.post(url, ans_content)

    distributed = get_distributed_queue(BATCH_ID['answer'])
    qid = re.search('http://zhidao.baidu.com/question/(\d+).html',url).group(1)
    for answer_id in answer_ids[:3]:
        answer_url = get_answer_url(qid, answer_id)
        put_url_enqueue(BATCH_ID['answer'], answer_url, distributed)

    return flag
