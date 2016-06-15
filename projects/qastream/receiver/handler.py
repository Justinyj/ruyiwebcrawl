#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web

class ZhidaoSearchHandler(tornado.web.RequestHandler):

    def get(self, qword):
        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

