#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web
from handler import ZhidaoSearchHandler

settings = {
# autoreload is incompatible with multi-process mode. When autoreload is enabled you must run only one process.
#    "autoreload": True,
#    "debug": True,
}

urls = tornado.web.Application([
    (r'/v1/zhidaosearch/(.+)', ZhidaoSearchHandler),
], **settings)
