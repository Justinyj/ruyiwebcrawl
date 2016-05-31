#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

#from selenium import webdriver
import requests
import time
import sys

from header import choice_agent, choice_proxy
from cache import Cache
from proxy import Proxy

class Downloader(object):

    def __init__(self, request=False, gap=0, batch_id='', groups=None, refresh=False):
        """ batch_id can be 'zhidao', 'music163', ...
        """
        self.request = request
        self.TIMEOUT = 10
        self.RETRY = 3

        self.gap = gap
        self.cache = Cache(batch_id)
        self.groups = groups
        self.refresh = refresh


    def login(self):
        if self.request is True:
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=self.RETRY))
            session.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
            }
            self.driver = session

        else:
            self.driver = webdriver.Firefox()
            self.driver.implicitly_wait(30)
            time.sleep(5)

    def close(self):
        if self.request is False:
            self.driver.quit()

    def update_header(self, header):
        if self.request is True:
            self.driver.headers.update(header)


    def pick_cookie_agent_proxy(self, url):
        self.driver.headers['User-Agent'] = choice_agent()

        proxies = choice_proxy(url, self.gap)
        self.driver.proxies.update(proxies)
        return proxies

    def _get_sleep_period(self):
        """ sleep for cookie
        """
        return 0

    def request_download(self, url, method='get', data=None):
        for i in range(self.RETRY):
            proxies = self.pick_cookie_agent_proxy(url)

            try:
                if method == 'post':
                    response = self.driver.post(url, timeout=self.TIMEOUT, data=data)
                else:
                    response = self.driver.get(url, timeout=self.TIMEOUT)
                    if response.status_code == 200:
                        return response.text #unicode
            except:
                proxy = proxies.items()[0][1]
                Proxy.instance().post(url, proxy)
                print('requests failed: ', sys.exc_info()[0])
            finally:
                time.sleep(self._get_sleep_period())
        else:
            return u''

    def selenium_download(self, url):
        for i in range(self.RETRY):
            try:
                self.driver.get(url)
                source = self.driver.page_source # unicode
                return source
            except:
                continue
            finally:
                time.sleep(self._get_sleep_period())
        else:
            return u''

    def requests_with_cache(self, url, method='get', encode='utf-8', groups=None, refresh=None, data=None):

        def save_cache(url, source, groups, refresh):
            refresh = self.refresh if refresh is None else refresh
            groups = self.groups if groups is None else groups
            ret = self.cache.post(url, source, groups, refresh)
            if ret not in [True, False]:
                print(ret)

        content = self.cache.get(url)
        if content != u'':
            return content

        if self.request is True:
            source = self.request_download(url, method, data)
            if source == u'':
                return source
            source = source.encode(encode)
            save_cache(url, source, groups, refresh)

        else:
            source = self.selenium_download(url)
            if source == u'':
                return source
            source = source.encode(encode)
            save_cache(url, source, groups, refresh)

        return source

