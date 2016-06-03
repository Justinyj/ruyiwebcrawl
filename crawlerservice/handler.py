#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.web
import base64
import json

from cache.basecache import BaseCache
from proxy.proxypool import ProxyPool
from fetch.downloader import Downloader
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

            url = base64.urlsafe_b64decode(b64url.encode('utf-8'))
            proxy = ProxyPool.instance().get(url, float(max_last_time))
            if proxy is None:
                response = {'success': False, 'error': 'no proxy avaiable'}
            else:
                response = {'success': True, 'proxy': proxy}
        except MissingParameter as e:
            response = {'success': False, 'error': e}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


    def post(self, b64url, useless):
        """
        :param proxy: e.g. 'http://8.8.8.8:8000'
        :param status: 'success' or 'fail'
        """
        try:
            proxy = self.get_body_argument(u'proxy', u'')
            status = self.get_body_argument(u'status', u'')
            if not proxy or not status:
                raise MissingParameter('missing parameter proxy or status')

            url = base64.urlsafe_b64decode(b64url.encode('utf-8'))
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
            _pool, ds = ProxyPool.instance().get_data_structure()
            response = {'success': True, 'pool': _pool, 'datastructure': ds}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


class FetchHandler(tornado.web.RequestHandler):
    def get(self, method, b64url):
        try:
            json_data = json.loads(self.request.body)
            batch_id = json_data.get(u'batch_id', u'').encode('utf-8')
            gap = json_data.get(u'gap', 0)
            header = json_data.get(u'header', {})
            js = json_data.get(u'js', False)
            encode = json_data.get(u'encode', u'utf-8').encode('utf-8')
            redirect_check = json_data.get(u'redirect_check', False)
            error_check = json_data.get(u'error_check', False)
            data = json_data.get(u'data', {}) # used in post
            refresh = json_data.get(u'refresh', False)

            if not js:
                downloader = Downloader(request=True,
                                        gap=gap,
                                        batch_id=batch_id)
                downloader.login()
                if header:
                    downloader.update_header(header)

                url = base64.urlsafe_b64decode(b64url.encode('utf-8'))
                if method.lower() == u'post':
                    if data:
                        ret = downloader.requests_with_cache(url, 'post', encode, redirect_check, error_check, data, refresh=refresh)
                    else:
                        ret = downloader.requests_with_cache(url, 'post', encode, redirect_check, error_check, data, refresh=refresh)
                else:
                    ret = downloader.requests_with_cache(url, 'get', encode, redirect_check, error_check, data, refresh=refresh)

            response = {'success': False, 'source': ret}
        except Exception as e:
            response = {'success': False, 'error': e}

        self.write(response)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

