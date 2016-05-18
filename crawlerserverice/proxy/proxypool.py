#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#

from __future__ import print_function, division

from collections import defaultdict
from Queue import PriorityQueue, Empty, Full
import urlparse
import time


class ProxyPool(object):
    """
        We assume proxy provider server a lot of freshed proxy all the time.
        1. We don't need to add a blacklist of ip:port to avoid freshed proxy unusable,
        2. We also don't need to recover blacklist ip:port back when pool becomes shallow.

        Calculate something in distributed crawlers to reduce burden of proxy server
            a. count max_last_time in crawlers
            b. count domain in crawlers (need this to fullfill the service)
    """
    def __init__(self):
        self._pool = set() # (url1, url2, ...)
        self._table = defaultdict(dict)

        self.FAIL_THRESHOLD = 5 # times
        self.FAILED = 0
        self.SUCCESS = 1



    def set_host_interval(self, host, interval):
        """.. :py:method::
            different sites set to different interval.
            e.g. {'baidu.com': 5, 'zhidao.baidu.com': 2}

        :param host: e.g. baidu.com
        :param interval: unit second
        """
        self._specific_interval[host] = interval


    def get_proxies(self):
        """ get proxies to pool
        """
        import requests
        api = 'http://proxy.mimvp.com/api/fetch.php?orderid=q_0_0_p@yahoo.com&num=20&result_fields=1,2&result_format=json'
        response = requests.get(api)


    def check_proxies(self):
        """ if proxy work, add to pool
        """
        pass

    def data_struct(self):
        """ {Domain: {Proxy1: (last_time, failed_count),
                      Proxy2: (last_time, failed_count),
                      priority: PriorityQueue()
                     }, ...
            }
        """
        pass


    def get(self, url, max_last_time):
        domain = urlparse.urlparse(url).netloc
        proxies_table = self._table[domain]
        now = time.time()

        rest_proxies = self._pool.difference( set(proxies_table.keys()) )
        if len(rest_proxies) == 0:
            try:
                item = proxies_table['priority'].get_nowait()
                last_time, failed_count, proxy = item
                if max_last_time < last_time:
                    proxies_table['priority'].put_nowait(item)
                    return
                proxies_table['priority'].put_nowait( (now, failed_count, proxy) )
                return proxy
            except Empty:
                print('queue is empty.')
            except Full:
                print('queue is full.')
        else:
            proxy = rest_proxies.pop()
            proxies_table[proxy] = (now, 0)

            if 'priority' not in proxies_table:
                proxies_table['priority'] = PriorityQueue()
            proxies_table['priority'].put_nowait( (now, 0, proxy) )
            return proxy


#        to_sleep = 0
#        if host in self._host_last_access_time:
#            interval = self._specific_interval[host] \
#                if host in self._specific_interval else self._interval
#
#            to_sleep = now - (self._host_last_access_time[host] + interval)
#            to_sleep = -to_sleep if to_sleep < 0 else 0
#
#        self._host_last_access_time[host] = now + to_sleep
#        return (proxy, to_sleep)


    def set_proxy_state(self, url, proxy, state):
        """.. :py:method::
            check whether proxy is available, and set
        """
        domain = urlparse.urlparse(url).netloc
        proxies_table = self._table[domain]

        if state == self.FAILED:
            if proxy in proxies_table:
                last_time, failed_count = proxy_table[proxy]
                failed_count += 1
                if failed_count >= self.FAIL_THRESHOLD:
                    proxies_table.pop(proxy)
                    self._pool.remove(proxy)
            else:
                proxy_table[proxy] = (now, 1)
        elif state == self.SUCCESS:
            pass


