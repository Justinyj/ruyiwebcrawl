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
         		"gap": 3,
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

        return False
