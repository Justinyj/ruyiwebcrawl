#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import tornado.web

from stream_process import QUEUE, return_best_answer
from parsers.zhidao_parser import parse_search_json_v0615
from hzlib import libregex

class ZhidaoSearchHandler(tornado.web.RequestHandler):


    def get(self, qword):

        if libregex.is_question_baike(qword):
            QUEUE.put(qword)
            ret = {'success': True}

            qapair = return_best_answer(qword)
            if qapair:
                ret["best_qapair"] = qapair

            self.write(ret)
        else:
            self.write({'success': False})
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
