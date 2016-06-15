#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import urllib

from .zhidao_downloader import zhidao_download
from .zhidao_parser import *
from downloader.cache import Cache

BATCH_ID = {
    'search': 'zhidao-search-20160614',
    'question': 'zhidao-question-20160614',
    'answer': 'zhidao-answer-20160614',
    'json': 'zhidao-json-20160614',
}


class Scheduler(object):

    def __init__(self):
        self.cache = Cache(BATCH_ID['json'])

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', cls())
        return cls._instance


    def zhidao_results(self, qids, gap, timeout=10):
        q_jsons = []
        for qid in qids:
            ret = self.zhidao_question(qid, gap, timeout)
            if ret is False:
                continue
            q_json, answer_ids = ret
            q_json['answers'] = []

            for rid in answer_ids[:3]:
                a_json = self.zhidao_answer(qid, rid, gap, timeout)
                if a_json is False:
                    continue
                q_json['answers'].append(a_json)

            q_jsons.append(q_json)
        return q_jsons


    def zhidao_question(self, qid, gap, timeout):
        question_url = 'http://zhidao.baidu.com/question/{}.html'.format(qid)
        ret = zhidao_download(question_url, BATCH_ID['question'], gap, timeout=timeout)
        if ret is False:
            return False
        answer_ids = []
        q_json = generate_question_json(qid, ret, answer_ids)
        if q_json is None:
            return False
        success = self.cache.post(question_url, q_json)
        return (q_json, answer_ids)


    def zhidao_answer(self, qid, rid, gap, timeout):
        answer_url = ('http://zhidao.baidu.com/question/api/mini?qid={}'
                      '&rid={}&tag=timeliness'.format(qid, rid))

        ret = zhidao_download(answer_url, BATCH_ID['answer'], gap, timeout=timeout, error_check=False)
        if ret is False:
            return False
        try:
            a_json = generate_answer_json(ret)
        except:
            return False

        success = self.cache.post(answer_url, a_json)
        return a_json


    def zhidao_search(qword, batch_id, gap=3, timeout=10):
        quote_word = urllib.quote(qword.encode('utf-8')) if isinstance(qword, unicode) else urllib.quote(qword)
        query_url = 'http://zhidao.baidu.com/index/?word={}'.format(quote_word)
#    query_url = 'http://zhidao.baidu.com/search?word={}'.format(quote_word)

        ret = zhidao_download(query_url, batch_id, gap, timeout=timeout, encode='utf-8', error_check=False)
        # resp.headers: 'content-type': 'text/html;charset=UTF-8',
        # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
        if ret is False:
            return False
        return zhidao_search_parse_qids(ret)


    def run(self, qword, gap=3, timeout=10):
        qids = zhidao_search(qword, BATCH_ID['search'], gap, timeout)
        return self.zhidao_results(qids, gap, timeout)

