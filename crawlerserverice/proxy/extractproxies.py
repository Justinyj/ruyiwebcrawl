#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time

import tornado.httpclient
import tornado.gen
import pycurl
try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient
except ImportError:
    from tornado.simple_httpclient import SimpleAsyncHTTPClient as AsyncHTTPClient

class ExtractProxies(object):
    def __init__(self):
        self.TESTURL = 'http://www.baidu.com'
        self.CONNECTIVITY_TEST = 3 # times
        self.TIMEOUT = 10
        self.SUCCESS_RATIO = 0.5

        self.limit = 200000
        self.every_time_num = 1 # 2000 max
        self.times_count = 0


    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls()
        return cls._instance


    def get_proxies(self):
        """ get proxies to pool
        """
        self.times_count += 1
        if self.times_count > self.limit / self.every_time_num:
            return

        api = ("http://proxy.mimvp.com/api/fetch.php?orderid=1915654268662414&"
               "num={}&country_group=1&http_type=1&anonymous=5&result_fields="
               "1,2&result_format=json".format(self.every_time_num))

        for i in range(5):
            try:
                response = requests.get(api)
                if response.status_code == 200:
                    break
            except Exception as e:
                pass
            time.sleep(5)
        return response.json()[u'result']


    def parse_proxies(self, item):
        proxies = {}
        for protocol in item[u'http_type'].split(u'/'):
            if u'HTTP' == protocol:
                proxies['http'] = 'http://' + item[u'ip:port'].encode('utf-8')
            elif u'HTTPS' == protocol:
                proxies['https'] = 'https://' + item[u'ip:port'].encode('utf-8')
            elif u'Socks5' == protocol:
                proxies['http'] = 'socks5://' + item[u'ip:port'].encode('utf-8')
        return proxies


    def check_proxies_connectivity(self, proxies):
        """ if proxy work, add to pool
        """
        success_count = self.SUCCESS_RATIO * self.CONNECTIVITY_TEST
        fail_count = self.CONNECTIVITY_TEST - success_count
        for i in range(self.CONNECTIVITY_TEST):
            try:
                response = requests.get(self.TESTURL,
                                        proxies=proxies,
                                        timeout=self.TIMEOUT)
                if response.status_code == 200:
                    success_count -= 1
                    if success_count <= 0:
                        return True
            except requests.ConnectionError:
                fail_count -= 1
            except requests.ReadTimeout:
                fail_count -= 1
            if fail_count <= 0:
                return False
        return



    def parse_proxies_async(self, item):
        proxies = {}
        for protocol in item[u'http_type'].split(u'/'):
            print(protocol)
            if u'HTTP' == protocol:
                proxies[pycurl.PROXYTYPE_HTTP] = item[u'ip:port'].encode('utf-8').split(':')
            elif u'Socks5' == protocol:
                proxies[pycurl.PROXYTYPE_SOCKS5] = item[u'ip:port'].encode('utf-8').split(':')
            elif u'Socks4' == protocol:
                proxies[pycurl.PROXYTYPE_SOCKS4] = item[u'ip:port'].encode('utf-8').split(':')
        return proxies


    @tornado.gen.coroutine
    def async_http(self, proxy):
        self.success_count = self.SUCCESS_RATIO * self.CONNECTIVITY_TEST
        self.fail_count = self.CONNECTIVITY_TEST - self.success_count

        for protocol, ip_port in proxy.items():
            host, port = ip_port
            if protocol == pycurl.PROXYTYPE_HTTP:
                pass
            elif protocol == pycurl.PROXYTYPE_SOCKS5:
                pass
            elif protocol == pycurl.PROXYTYPE_SOCKS4:
                pass
            else:
                yield

        def prepare_curl_type(curl):
            curl.setopt(pycurl.PROXYTYPE, protocol)

        def handle_request(response):
            # TODO no response here, don't know why
            print(response.code)
            if response.code == 200:
                self.success_count -= 1
            else:
                self.fail_count -= 1


        AsyncHTTPClient.configure(
                'tornado.curl_httpclient.CurlAsyncHTTPClient')
        http_client = AsyncHTTPClient()
        http_request = tornado.httpclient.HTTPRequest(
                url=self.TESTURL,
                method='GET',
                proxy_host=host,
                proxy_port=int(port),
                prepare_curl_callback=prepare_curl_type,
                follow_redirects=False,
        )

        for i in range(self.CONNECTIVITY_TEST):
            http_client.fetch(http_request, self.handle_request)

        while True:
            print(self.success_count, self.fail_count)
            time.sleep(1)
            if self.success_count <= 0:
                raise tornado.gen.Return(True)
            if self.fail_count <= 0:
                raise tornado.gen.Return(False)


def extract_proxies():
    """
    :rtype: [{'http': 'http://123.169.238.33:8888'}, ...]
    """
    instance = ExtractProxies.instance()
    requests_proxies = []
    raw_proxies = instance.get_proxies()
    if raw_proxies is not None:
        for item in raw_proxies:
            proxies = instance.parse_proxies(item)
            ret = instance.check_proxies_connectivity(proxies)
            if ret is True:
                requests_proxies.append(proxies)
    return requests_proxies


def extract_proxies_async():
    """
    :rtype: [{'http': 'http://123.169.238.33:8888'}, ...]
    """
    instance = ExtractProxies.instance()
    requests_proxies = []
    raw_proxies = instance.get_proxies()
    if raw_proxies is not None:
        for item in raw_proxies:
            proxies = instance.parse_proxies_async(item)
            ret = instance.async_http(proxies)
            if ret is True:
                requests_proxies.append(proxies)
    return requests_proxies

