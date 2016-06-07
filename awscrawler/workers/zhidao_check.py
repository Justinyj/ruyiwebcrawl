#-*- coding:utf-8 -*-

import os
import sys
import re
import json
import base64
import traceback
import logging
import requests
import time
from invoker.zhidao import BATCH_ID, HEADER
from zhidao_tools import get_zhidao_content
OUTPUT_FILE = 'OUTPUT'

def check_question(question_raw):
    question = json.loads(question_raw)
    count = len(question['answers'][:3])
    count = min(3, count)
    answers = []
    for ans_id in question['answers']:
        tmp = Cache(BATCH_ID['result'])
        url = get_answer_url(question['question_id'], answer['ans_id'])
        flag = tmp.get(url, exist=True)
        if not flag:
            continue
        answer_content = m.get(get_answer_url(
            question['question_id'], answer['ans_id']))
        if answer_content == None:
            continue
        answer = json.loads(answer_content)
        if (answer['question_id'] == question['question_id']):
            count -= 1
            answers.append(answer)
            if (count == 0):
                break
    if answers == '':
        print "此题无答案或获取答案失败"
        return
    if count:
        print "无法获取所有答案"
    result = {'question': question, 'answers': answers}
    # question is a dict,answers is list of dicts
    result = json.dumps(result)

    m = Cache(BATCH_ID['result'])
    url = get_question_url(question['question_id'])
    flag = m.post(url, result)


def check_url(url):
    m = Cache(BATCH_ID['json'])
    question_raw = m.get(url)
    check_question(question_raw)
