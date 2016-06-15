#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import base64
import urlparse
import requests

CACHE_SERVER = 'http://192.168.1.179:8000'

class Cache(object):
    def __init__(self, batch_id, server=None):
        self.server = server if server else CACHE_SERVER
        self.batch_id = batch_id

    def get(self, url, exists=False):
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/cache/{}/{}'.format(b64url, self.batch_id)
        get_api_url = urlparse.urljoin(self.server, api_url)

        response = requests.get(get_api_url, data={'exists': False})

        js = response.json()
        if js[u'success'] is False:
            return u''

        if exists:
            return js[u'exists']
        return js[u'content']

    def post(self, url, content, groups=None, refresh=False):
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/cache/{}/{}'.format(b64url, self.batch_id)
        post_api_url = urlparse.urljoin(self.server, api_url)

        data = {
            'groups': groups,
            'content': content,
            'refresh': refresh,
        }

        ret = False
        for _ in range(2):
            response = requests.post(post_api_url, data=data)
            if response.status_code != 200:
                ret = response.content
                continue

            js = response.json()
            if js['success'] is True:
                return True
            if u'error' in js:
                ret = js[u'error']
                continue
        return ret
