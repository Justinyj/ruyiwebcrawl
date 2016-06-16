#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import tornado.web

from stream_process import QUEUE
from parsers.zhidao_parser import parse_search_json_v0615


class ZhidaoSearchHandler(tornado.web.RequestHandler):

    def __init__(self):
        self.config = {
             "batch_ids": {
                 "search": "zhidao-search-20160614",
                 "question": "zhidao-question-20160614",
                 "answer": "zhidao-answer-20160614",
                 "json": "zhidao-json-20160614"
             },
             "cache_server": "http://52.192.116.149:8000",
             "http_headers": {
                 "Host": "zhidao.baidu.com"
             },
             "crawler": {
                 "gap": 2,
                 "timeout": 2,
                 "encoding": "gb18030",
                 "error_check": True
             }
        }

    def get(self, qword):
        if qword:
            QUEUE.put(qword)

            ret = {'success': True }
            qapair = self.zhidao_search(qword)
            if qapair:
                ret["best_qapair"] = qapair
            self.write(ret)
        else:
            self.write({'success': False})
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def zhidao_search(self, qword):
        if isinstance(qword, unicode):
            qword = qword.encode("utf-8")

        qword_url = "http://zhidao.baidu.com/search/?word={}".format( urllib.quote(qword) )

        ret = self.downloader.downloader_wrapper(
                qword_url,
                self.config["batch_ids"]["search"],
                self.config["crawler"]["gap"],
                timeout=self.config["crawler"]["timeout"],
                encoding=self.config["crawler"]["encoding"])

        if ret is False:
            return False

        # parse
        search_result_json = parse_search_json_v0615(ret)

        # get the best answer
        for item in search_result_json.values():
            if item["rtype"] == "recommend":
                return item
                
        """
        sample output
        {
            "a_summary": "李时珍。资料如下：《本草纲目》，药学著作，五十二卷，明·李时珍撰，刊于1590年。全书共190多万字，载有药物1892种，收集医方11096个，绘制精美插图1160幅，分为16部、60类。是作者在继承和总结以前本草学成就的基础上，结合作者长期学习、采访所积累的大量药学知识，经过实践和钻研，历时数十年而编成的一部巨著。书中不仅考正了过去本草学中的若干错误，综合了大量科学资料，提出了较科学的药物分类方法，溶入先进的生物进化思想...",
            "cnt_answer": 0,
            "cnt_like": 7,
            "qid": "254975433",
            "question": "《本草纲目》的作者是谁？",
            "question_good": false,
            "rank": 0,
            "rtype": "recommend"
        }
        """
        return False
