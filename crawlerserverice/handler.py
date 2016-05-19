#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web
import tornado.escape
import base64

from cache.basecache import BaseCache
from proxy.proxypool import ProxyPool
import exception

class MissingParameter(Exception): pass

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



class ProxyHandler(tornado.web.RequestHandler):
    def get(self, b64url, max_last_time):
        """
        :rtype proxy: {'http', 'http://8.8.8.8:8000'}
        """
        try:
            if max_last_time is None:
                raise MissingParameter('missing parameter max_last_time')

            url = base64.urlsafe_decode(b64url.encode('utf-8'))
            proxy = ProxyPool.instance().get(url, float(max_last_time))
            response = {'success': True, 'proxy': proxy}
        except MissingParameter as e:
            response = {'success': False, 'error': e}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


    def post(self, b64url):
        """
        :param proxy: e.g. 'http://8.8.8.8:8000'
        :param status: 'success' or 'fail'
        """
        try:
            proxy = self.get_body_argument(u'proxy', u'')
            status = self.get_body_argument(u'status', u'')
            if not proxy or not status:
                raise MissingParameter('missing parameter proxy or status')

            url = base64.urlsafe_decode(b64url.encode('utf-8'))
            ProxyPool.instance().set_proxy_status(url, proxy, status)
            response = {'success': True}
        except MissingParameter as e:
            response = {'success': False, 'error': e}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


class ProxyDataStructureHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            ds = ProxyPool.instance().get_data_structure()
            response = {'success': True, 'datastructure': ds}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

