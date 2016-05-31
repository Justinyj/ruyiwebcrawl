#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import base64
import urlparse
import requests

from settings import PROXY_SERVER

class Proxy(object):
    def __init__(self, server=None):
        self.server = server if server else PROXY_SERVER

    @classmethod
    def instance(cls, server=None):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', cls(server))
        return cls._instance

    def get(self, url, max_last_time):
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/proxy/{}/{}'.format(b64url, max_last_time)
        get_api_url = urlparse.urljoin(self.server, api_url)

        response = requests.get(get_api_url)

        js = response.json()
        if js[u'success'] is True:
            return js[u'proxy']
        return False


    def post(self, url, proxy):
        """ 'proxy': 'http://101.96.11.36:80',
        """
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/proxy/{}'.format(b64url)
        post_api_url = urlparse.urljoin(self.server, api_url)

        data = {
            'proxy': proxy,
            'status': 'fail',
        }

        response = requests.post(post_api_url, data=data)

        js = response.json()
        if js['success'] is True:
            return True
        if u'error' in js:
            return js[u'error']
        return False
