#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web
from handler import *
from prefetch_handler import *

settings = {
# autoreload is incompatible with multi-process mode. When autoreload is enabled you must run only one process.
#    "autoreload": True,
#    "debug": True,
}

urls = tornado.web.Application([
    (r'/v1/cache/([a-zA-Z0-9=\-_]+)/?([a-zA-Z0-9_]*)', CacheHandler),

    (r'/v1/proxy/datastructure/?', ProxyDataStructureHandler),
    (r'/v1/proxy/([a-zA-Z0-9=\-_]+)/?(\d+\.?\d*)?', ProxyHandler),


    (r'/v1/prefetch/(?P<batch_id>[a-zA-Z0-9_]+)/(?P<method>[a-zA-Z]+)', PrefetchHandler),

    (r'/v1/fetch/(?P<method>[a-zA-Z]+)/(?P<b64url>[a-zA-Z0-9=\-_]+)', FetchHandler),
], **settings)
