#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue
from __future__ import print_function, division
import time
import os
import sys
import re
import base64
import traceback
import requests

from invoker.zhidao import BATCH_ID, HEADER
from downloader.cache import Cache
from .zhidao_tools import get_zhidao_content, get_answer_url
from .zhidao_parser import parse_title, parse_q_time, parse_q_content, parse_answer_ids, generate_question_json



def process(url, parameter, manager, *args, **kwargs):
    m = re.search(
<<<<<<< HEAD
        '<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is None:
        return
    q_time = m.group(1)
    return q_time


def parse_q_content(content):
    q_content = ''
    m = re.search('accuse="qContent">(.*?)(</pre>|</div>)', content)
    n = re.search('accuse="qSupply">(.*?)(</pre>|</div>)', content)
    if m:
        q_content = m.group(1)
        q_content = re.sub('<.*?>', '\n', q_content)
        q_content = q_content.strip()
    if n:
        supply = n.group(1)
        q_content += supply
    if q_content:
        return q_content
    return


def parse_answer_ids(content):
    res=[]
    pro = re.search('id="answer-(/d+)" class="answer quality-info line">')
    if pro :
        res.append(pro.group(1))
    answers=re.findall('class="bd answer.*" id="answer-(\d+)"',content)
    res.extend(map(int,answers))
    return res


def generate_question_json(content, answer_ids):
    q_title = parse_title(content)
    if q_title is None:
        # print('未找到title或者页面不存在')
        return
    q_id = parse_q_id(content)
    q_content = parse_q_content(content)
    if 'word-replace' in q_content:
        #   setattr(generate_question_json, '_imgcontent_counter', 0)
        #generate_question_json._imgcontent_counter += 1
        return
    q_time = parse_q_time(content)
    rids = parse_answer_ids(content)
    item = {
        'question_id': q_id,
        'question_title': q_title,
        'question_detail': q_content,
        'question_time': q_time,
        'answers': rids,
    }
    answer_ids.extend(rids)
    return json.dumps(item)

=======
        'http://zhidao.baidu.com/question/(\d+).html', url)
    if not m:
        return False
>>>>>>> 54994b8312ecc11bba8342e40aaa15f5a87dc4c7

    q_id = m.group(1)
    method, gap, js, data = parameter.split(':')
    gap = int(gap)
    batch_id = BATCH_ID['question']

    for _ in range(2):
        content = get_zhidao_content(url, method, gap, HEADER, batch_id)
        if content != u'':
            break
        time.sleep(gap)
    else:
        return False

    answer_ids = []
    question_content = generate_question_json(q_id, content, answer_ids)
    if question_content is None:
        return False

    m = Cache(BATCH_ID['json'])
    success = m.post(url, question_content)
    if success is False:
        return False

    answer_urls = []
    for answer_id in answer_ids[:3]:
        answer_urls.append( get_answer_url(q_id, answer_id) )
    manager.put_urls_enqueue(BATCH_ID['answer'], answer_urls)

    return True
