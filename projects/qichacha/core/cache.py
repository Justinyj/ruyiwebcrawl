#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import base64
import urlparse
import requests

class Cache(object):
    def __init__(self, config, batch_id, server=None):
        self.SERVER = server if server else config['CACHE_SERVER']
        self.batch_id = batch_id

    def get(self, url):
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/cache/{}/{}'.format(b64url, self.batch_id)
        get_api_url = urlparse.urljoin(self.SERVER, api_url)

        response = requests.get(get_api_url)

        js = response.json()
        if js[u'success'] is False:
            return u''
        return js[u'content']


    def post(self, url, content, groups=None, refresh=False):
        b64url = base64.urlsafe_b64encode(url)
        api_url = 'v1/cache/{}/{}'.format(b64url, self.batch_id)
        post_api_url = urlparse.urljoin(self.SERVER, api_url)

        data = {
            'groups': groups,
            'content': content,
            'refresh': refresh,
        }
        response = requests.post(post_api_url, data=data)

        js = response.json()
        if js['success'] is True:
            return True
        if u'error' in js:
            return js[u'error']
        return False
