#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from .zhidao_search import zhidao_search, HEADERS
from .zhidao_parser import *

'zhidao-search-20160614'
'zhidao-question-20160614'
'zhidao-answer-20160614'
cache_server = '192.168.1.179:8000'

def zhidao_results(qids, timeout=10):
    for qid in qids:
        question_url = 'http://zhidao.baidu.com/question/{}.html'.format(qid)
        resp = requests.get(question_url, headers=HEADERS, timeout=timeout)



def run(word, timeout=10):
    qids = zhidao_search(word, timeout)
    zhidao_result(qids, timeout)
