#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time
import pycurl
from collections import deque

from tornado.locks import Semaphore
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from tornado import httpclient
from tornado import gen

from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient, CurlError


DAY_LIMIATION = 200000
ONCE_LIMIATION = 2000
CONCURRENT_NUM = 10


class ExtractProxies(object):
    def __init__(self):
        self.TESTURL = 'http://www.baidu.com'
        self.CONNECTIVITY_TEST = 3 # times
        self.TIMEOUT = 10
        self.SUCCESS_RATIO = 0.5

        self.limit = DAY_LIMIATION
        self.once_limit = ONCE_LIMIATION
        self.every_fetch_num = 1000
        assert self.once_limit >= self.every_fetch_num

        self.max_fetch_times = self.limit / self.every_fetch_num
        self.times_count = 0
        self.fetch_duration = 86400 / self.max_fetch_times


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
        if self.times_count > self.max_fetch_times:
            return

        api = ("http://proxy.mimvp.com/api/fetch.php?orderid=1915654268662414&"
               "num={}&country_group=1&http_type=1&anonymous=5&ping_time=0.3&transfer_time=1&result_fields="
               "1,2&result_format=json".format(self.every_fetch_num))

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
        """ pycurl not support https
        """
        proxies = {}
        for protocol in item[u'http_type'].split(u'/'):
            if u'HTTP' == protocol:
                proxies[pycurl.PROXYTYPE_HTTP] = ['http'] + item[u'ip:port'].encode('utf-8').split(':')
            elif u'Socks5' == protocol:
                proxies[pycurl.PROXYTYPE_SOCKS5] = ['socks5'] + item[u'ip:port'].encode('utf-8').split(':')
            # elif u'Socks4' == protocol:
            #     proxies[pycurl.PROXYTYPE_SOCKS4] = ['socks4'] + item[u'ip:port'].encode('utf-8').split(':')
        return proxies


    @gen.coroutine
    def async_http(self, proxy, idx, requests_proxies):
        success_count = self.SUCCESS_RATIO * self.CONNECTIVITY_TEST
        fail_count = self.CONNECTIVITY_TEST - success_count
        count = {} # callback of async_httpclient(handle_request) get local variable,
                   # no conflict with multi coroutine
        count[idx] = [success_count, fail_count]

        for protocol, pro_ip_port in proxy.items():
            pro_type, host, port = pro_ip_port
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

        @gen.coroutine
        def handle_request(response):
            if response.code == 200:
                count[idx][0] -= 1
            else:
                count[idx][1] -= 1


        AsyncHTTPClient.configure(
                'tornado.curl_httpclient.CurlAsyncHTTPClient')
        http_client = AsyncHTTPClient()
        http_request = httpclient.HTTPRequest(
                url=self.TESTURL,
                method='HEAD',
                proxy_host=host,
                proxy_port=int(port),
                prepare_curl_callback=prepare_curl_type,
                follow_redirects=False,
        )

        for i in range(self.CONNECTIVITY_TEST):
            try:
                response = yield http_client.fetch(http_request, handle_request)
            except CurlError as e:
                print('Curl Error: ', e)

        while True:
            gen.sleep(0.01)
            if count[idx][0] <= 0:
                if pro_type == 'https':
                    requests_proxies.append({'https': '{}://{}:{}'.format(pro_type, host, port)})
                else:
                    requests_proxies.append({'http': '{}://{}:{}'.format(pro_type, host, port)})
                raise gen.Return(True)
            if count[idx][1] <= 0:
                raise gen.Return(False)



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
            requests_proxies.append(proxies)
#            ret = instance.check_proxies_connectivity(proxies)
#            if ret is True:
#                requests_proxies.append(proxies)
    return requests_proxies



futures_q = deque([Future() for _ in range(CONCURRENT_NUM)])

@gen.coroutine
def simulator(futures):
    for f in futures:
        yield gen.moment
        f.set_result(None)

IOLoop.current().add_callback(simulator, list(futures_q))

SEM = Semaphore(CONCURRENT_NUM)

@gen.coroutine
def worker(instance, idx, item, requests_proxies):
    with (yield SEM.acquire()):
        proxies = instance.parse_proxies_async(item)
        yield instance.async_http(proxies, idx, requests_proxies)


@gen.coroutine
def extract_proxies_async(requests_proxies):
    """
    :rtype: [{'http': 'http://123.169.238.33:8888'}, ...]
    """
    instance = ExtractProxies.instance()
    raw_proxies = instance.get_proxies()
    if raw_proxies is not None:
        yield [worker(instance, idx, item, requests_proxies) \
            for idx, item in enumerate(raw_proxies)]

    print('\n*===================*\n')
