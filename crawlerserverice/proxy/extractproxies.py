#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests

class ExtractProxies(object):
    def __init__(self):
        self.TESTURL = 'http://www.baidu.com'
        self.CONNECTIVITY_TEST = 6 # times
        self.TIMEOUT = 20
        self.SUCCESS_RATIO = 0.5


    def get_proxies(self):
        """ get proxies to pool
        """
        num = 1
        api = 'http://proxy.mimvp.com/api/fetch.php?orderid=1915654268662414&num={}&country_group=1&http_type=1&anonymous=5&result_fields=1,2&result_format=json'.format(num)
        for i in range(5):
            try:
                response = requests.get(api)
                if response.status_code == 200:
                    break
            except Exception as e:
                time.sleep(4)
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
        count = 0
        for i in range(self.CONNECTIVITY_TEST):
            try:
                response = requests.get(self.TESTURL,
                                        proxies=proxies,
                                        timeout=self.TIMEOUT)
                if response.status_code == 200:
                    count += 1
                    if count >= success_count:
                        return True
            except requests.ConnectionError:
                pass
            except requests.ReadTimeout:
                pass
        return False


    def run(self):
        requests_proxies = []
        raw_proxies = self.get_proxies()
        for item in raw_proxies:
            proxies = self.parse_proxies(item)
            ret = self.check_proxies_connectivity(proxies)
            if ret is True:
                requests_proxies.append(proxies)
        return requests_proxies

print( ExtractProxies().run() )
