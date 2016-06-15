#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import tornado.web

from stream_process import QUEUE


class ZhidaoSearchHandler(tornado.web.RequestHandler):

    def get(self, qword):
        if qword:
            QUEUE.put(qword)

            self.write({'success': True})
        else:
            self.write({'success': False})
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

