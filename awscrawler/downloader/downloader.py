#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

#from selenium import webdriver
import requests
import time
import sys

from .cache import Cache

class Downloader(object):

    def __init__(self, request=False, gap=0, batch_id='', groups=None, refresh=False):
        """ batch_id can be 'zhidao', 'music163', ...
        """
        self.request = request
        self.TIMEOUT = 10
        self.RETRY = 3

        self.gap = gap
        self.batch_key = batch_id.rsplit('-', 1)[0]
        self.cache = Cache(batch_id)
        self.groups = groups
        self.refresh = refresh


    def login(self):
        if self.request is True:
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=self.RETRY))
            session.headers = common_header
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

    def _get_sleep_period(self):
        """ sleep for cookie
        """
        return 0

    def request_download(self, url, method='get', encode='utf-8', redirect_check=False, error_check=False, data=None):
        for i in range(self.RETRY):

            try:
                if method == 'post':
                    response = self.driver.post(url, timeout=self.TIMEOUT, data=data)
                else:
                    response = self.driver.get(url, timeout=self.TIMEOUT)

                if response.status_code == 200:
                    if redirect_check and response.url != url:
                        continue
                    if error_check:
                        if __import__('fetch.error_checker.{}'.format(self.batch_key), fromlist=['error_checker']).error_checker(response):
                            continue
                    response.encoding = encode
                    return response.text # text is unicode
            except: # requests.exceptions.ProxyError, requests.ConnectionError, requests.ConnectTimeout
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

    def requests_with_cache(self,
                            url,
                            method='get',
                            encode='utf-8',
                            redirect_check=False,
                            error_check=False,
                            data=None,
                            groups=None,
                            refresh=None):

        def save_cache(url, source, groups, refresh):
            refresh = self.refresh if refresh is None else refresh
            groups = self.groups if groups is None else groups
            ret = self.cache.post(url, source, groups, refresh)
            if ret not in [True, False]:
                print(ret)

        if refresh is True:
            content = self.cache.get(url)
            if content != u'':
                return content

        if self.request is True:
            source = self.request_download(url, method, encode, redirect_check, error_check, data)
        else:
            source = self.selenium_download(url)

        if source == u'':
            return source
        save_cache(url, source, groups, refresh)

        return source

