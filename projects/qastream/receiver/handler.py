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
from hzlib import libregex

class ZhidaoSearchHandler(tornado.web.RequestHandler):

    def init(self, cacheserver):
        self.scheduler = Scheduler(cacheserver=cacheserver)

    def get(self, qword):

        if libregex.is_question_baike(qword):
            QUEUE.put(qword)
            ret = {'success': True}

            qapair = self.scheduler.zhidao_search_select_best(qword)
            if qapair:
                ret["best_qapair"] = qapair

            self.write(ret)
        else:
            self.write({'success': False})
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
