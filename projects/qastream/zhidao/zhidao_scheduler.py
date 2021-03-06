#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import urllib

from parsers.zhidao_parser import *
from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper

BATCH_ID = {
    'search': 'zhidao-search-20160614',
    'question': 'zhidao-question-20160614',
    'answer': 'zhidao-answer-20160614',
    'json': 'zhidao-json-20160614',
}

class Scheduler(object):

    def __init__(self, cacheserver):
        self.cache = Cache(BATCH_ID['json'], cacheserver)
        self.downloader = DownloadWrapper(cacheserver, {'Host': 'zhidao.baidu.com'})

    @classmethod
    def instance(cls, *args):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', cls(*args))
        return cls._instance


    def zhidao_results(self, qids, gap, timeout=10):
        q_jsons = []
        for qid in qids:
            q_json = self.zhidao_question(qid, gap, timeout)
            if q_json is False:
                continue
            q_json['list_answers'] = []

            for rid in q_json['answer_ids'][:3]:
                a_json = self.zhidao_answer(qid, rid, gap, timeout)
                if a_json is False:
                    continue
                q_json['list_answers'].append(a_json)

            q_jsons.append(q_json)
        return q_jsons


    def zhidao_question(self, qid, gap, timeout):
        question_url = 'http://zhidao.baidu.com/question/{}.html'.format(qid)
        ret = self.downloader.downloader_wrapper(question_url, BATCH_ID['question'], gap, timeout=timeout, encoding='gb18030', error_check=True)
        if ret is False:
            return False
        q_json = generate_question_json(qid, ret)
        if q_json is None:
            return False
        success = self.cache.post(question_url, q_json)
        return q_json


    def zhidao_answer(self, qid, rid, gap, timeout):
        answer_url = ('http://zhidao.baidu.com/question/api/mini?qid={}'
                      '&rid={}&tag=timeliness'.format(qid, rid))

        ret = self.downloader.downloader_wrapper(answer_url, BATCH_ID['answer'], gap, timeout=timeout, encoding='gb18030')
        if ret is False:
            return False
        try:
            a_json = generate_answer_json(ret)
        except:
            return False

        success = self.cache.post(answer_url, a_json)
        return a_json


    def zhidao_search(self, qword, batch_id, gap=3, timeout=10, refresh=True):
        quote_word = urllib.quote(qword.encode('utf-8')) if isinstance(qword, unicode) else urllib.quote(qword)
        # query_url = 'http://zhidao.baidu.com/index/?word={}'.format(quote_word) # utf-8
        query_url = 'http://zhidao.baidu.com/search?word={}'.format(quote_word)

        ret = self.downloader.downloader_wrapper(query_url, batch_id, gap, timeout=timeout, encoding='gb18030', refresh=refresh)
        # resp.headers: 'content-type': 'text/html;charset=UTF-8',
        # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
        if ret is False:
            return False
        return zhidao_search_questions(ret)

    def zhidao_search_list_json(self, qword, batch_id, gap=3, timeout=10, refresh=False):
        quote_word = urllib.quote(qword.encode('utf-8')) if isinstance(qword, unicode) else urllib.quote(qword)
        # query_url = 'http://zhidao.baidu.com/index/?word={}'.format(quote_word) # utf-8
        query_url = 'http://zhidao.baidu.com/search?word={}'.format(quote_word)

        ret = self.downloader.downloader_wrapper(query_url, batch_id, gap, timeout=timeout, encoding='gb18030', refresh=refresh)
        # resp.headers: 'content-type': 'text/html;charset=UTF-8',
        # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
        if ret is False:
            return False

        search_result_json = parse_search_json_v0615(ret)
        for item in search_result_json:
            item["query"] = qword
            if type(qword) != unicode:
                item["query"] = qword.decode("utf-8")

        return search_result_json

    def zhidao_search_select_best(self, qword, gap=3, timeout=2):
        search_result_json = self.zhidao_search_list_json(qword, BATCH_ID['search'], gap, timeout)

        # get the best answer
        for item in search_result_json:
            if item["is_recommend"] == 1:
                return item

        return False

    def zhidao_search_select_best_qids(self, qword, gap=3, timeout=2):
        ret = self.zhidao_search_select_best(qword, gap, timeout)
        if ret:
            return [ ret["question_id"] ]
        return []


    def run(self, qword, gap=3, timeout=10):
        # qids = self.zhidao_search(qword, BATCH_ID['search'], gap, timeout)
        qids = self.zhidao_search_select_best_qids(qword, gap, timeout)
        return self.zhidao_results(qids, gap, timeout)
