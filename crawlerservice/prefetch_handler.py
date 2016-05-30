#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json
import tornado.web


class PrefetchHandler(tornado.web.RequestHandler):
    def post(self, batch_id, method):
        """ transmit all urls once, because ThinHash depends on
            modulo algroithm, must calculate modulo in the begining.
            Can not submit second job with same batch_id before first job finished.
        """
        try:
            batch_id = batch_id.encode('utf-8')
            if Record.instance().is_finished(batch_id) is False:
                raise(Exception('job with same batch_id is not finished.'))

            gap = self.get_body_argument(u'gap', u'')
            js = self.get_body_argument(u'js', False)
            urls = self.get_body_arguments(u'urls')
            headers = self.get_body_arguments(u'headers') # [{}, {}]
            data = self.get_body_argument(u'data', {}) # used in post

            if not urls:
                raise(Exception('not transmit urls parameter'))

            parameter = '{method}:{gap}:{js}:{headers}:{data}'.format(
                    method=method.encode('utf-8'),
                    gap=gap.encode('utf-8'),
                    js=1 if js else 0,
                    headers=json.dumps(headers) if headers else '',
                    data=json.dumps(data) if data else '')

            total_count = len(urls)
            Record.instance().begin(batch_id, parameter, total_count)
            queue = HashQueue(batch_id, priority=2, timeout=90, failure_times=3)

            thinhash = ThinHash(batch_id, total_count)
            for url in urls:
                if isinstance(url, unicode):
                    url = url.encode('utf-8')
                field = int(hashlib.sha1(url).hexdigest(), 16)
                thinhash.hset(field, url)

                queue.put_init(field)

        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


class FetchHandler(tornado.web.RequestHandler):
    def post(self, method, b64url): # can be get either
        header = self.get_body_argument(u'header', u'')
        js = self.get_body_argument(u'js', False)


