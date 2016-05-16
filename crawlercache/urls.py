#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web
from handler import *

settings = {
    "autoreload": True,
}

urls = tornado.web.Application([
    (r'/v1/cache/([a-zA-Z0-9=\-_]+)/?([a-zA-Z0-9_]*)', CacheHandler),
], **settings)
