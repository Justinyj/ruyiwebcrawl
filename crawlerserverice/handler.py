#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import exception
import tornado.web
import tornado.escape

from cache.basecache import BaseCache

class CacheHandler(tornado.web.RequestHandler):

    @exception.exception
    def get(self, b64url, batch_id):
        response = BaseCache.get_cache(b64url.encode('utf-8'),
                                       batch_id.encode('utf-8'))
        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def post(self, b64url, batch_id):
        # x_real_ip = self.request.headers.get("X-Real-IP")
        # remote_ip = x_real_ip or self.request.remote_ip

        groups = self.get_body_argument(u'groups', u'')
        content = self.get_body_argument(u'content', u'')
        refresh = self.get_body_argument(u'refresh', False)

        response = BaseCache.set_cache(b64url.encode('utf-8'),
                                       batch_id.encode('utf-8'),
                                       groups.encode('utf-8'),
                                       content.encode('utf-8'),
                                       refresh)
        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

