#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#

from __future__ import print_function, division

from collections import defaultdict
from Queue import heapq
import json
import os
import time
import urlparse
import tornado.gen

from extractproxies import extract_proxies, extract_proxies_async
from settings import FSCACHEDIR

class ProxyPool(object):
    """
        We assume proxy provider server a lot of freshed proxy all the time.
        1. We don't need to add a blacklist of ip:port to avoid freshed proxy unusable,
        2. We also don't need to recover blacklist ip:port back when pool becomes shallow.
        3. We don't need to dump the data structure every 5 minutes, so we can recover from crash.

        Calculate something in distributed crawlers to reduce burden of proxy server
            a. count max_last_time in crawlers
            b. count domain in crawlers (need this to fullfill the service)
    """

    def __init__(self):
        """ self._table = {
                'Domain': {
                    'Proxy1': (last_time, count),
                    'Proxy2': (last_time, count),
                    'priority': PriorityQueue()
                }, ...
            }
            priority: (last_time, count, proxy)
        """
        self._pool = set() # (url1, url2, ...)
        self._table = defaultdict(dict)

        self.FAIL_THRESHOLD = 5 # times
        self.FAILED = u'fail'
        self.SUCCESS = u'success'


        self.dump_file = os.path.join(FSCACHEDIR, 'datastructure.dump')
        if os.path.isfile(self.dump_file):
            with open(self.dump_file) as fd:
                self._pool, self._table = json.load(fd)
            self._pool = set(self._pool)
            self._table = defaultdict(dict, self._table)

        self.extract_proxies_task_async()

    @tornado.gen.coroutine
    def extract_proxies_task(self):
        while True:
            requests_proxies = extract_proxies()
            for proxy in requests_proxies:
                for protocol, address in proxy.items():
                    self._pool.add(address)
            yield tornado.gen.sleep(432)



    @tornado.gen.coroutine
    def extract_proxies_task_async(self):
        requests_proxies = set()
        while True:
            # TODO yield fetch_duration next line
            extract_proxies_async(requests_proxies)
            for proxy in requests_proxies:
                self._pool.add(proxy)
            yield tornado.gen.sleep(300) # 432


    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls()
        return cls._instance


    def set_host_interval(self, host, interval):
        """.. :py:method::
            different sites set to different interval.
            e.g. {'baidu.com': 5, 'zhidao.baidu.com': 2}

        :param host: e.g. baidu.com
        :param interval: unit second
        """
        self._specific_interval[host] = interval


    def _count_rule(self, method, count):
        """ get count negative, set count positive, count begin with 0.

            Now, crawler only set status after proxy failed,
            so every get, assume proxy works, count -= 1,
            every set, means proxy don't work, count += 2,
            Failer after many success, reset count = 0
        """
        if method == 'get':
            count -= 1
        elif method == 'set':
            count = count + 2 if count >= 0 else 0
        return count


    def get(self, url, max_last_time):
        """ proxy is the form http://8.8.8.8:8000

            if self._pool not all in self._table[domain]:
                add one of the difference to self._table[domain]
            else:
                pop item with lowest last_time from priority queue,
                compare last proxied time,
                if no proxy available, put item back, return None.
                else, put item back with now time, update self._table[domain][proxy], return proxy
        """
        domain = urlparse.urlparse(url).netloc
        proxies_table = self._table[domain]
        now = time.time()

        if not self._pool:
            return
        rest_proxies = self._pool.difference( set(proxies_table.keys()) )

        if len(rest_proxies) == 0:
            try:
                item = heapq.heappop(proxies_table['priority'])
                last_time, count, proxy = item
                if max_last_time < last_time:
                    heapq.heappush(proxies_table['priority'], item)
                    return

                _count = self._count_rule('get', count)
                proxies_table[proxy] = [now, _count]
                heapq.heappush(proxies_table['priority'], [now, _count, proxy])
                return proxy
            except IndexError:
                print('priority queue is empty.')
        else:
            count = 0
            _count = self._count_rule('get', count)
            proxy = rest_proxies.pop()
            proxies_table[proxy] = [now, _count]

            if 'priority' not in proxies_table:
                proxies_table['priority'] = []
            heapq.heappush(proxies_table['priority'], [now, _count, proxy])
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


    def set_proxy_status(self, url, proxy, status):
        """.. :py:method::
            Now, crawler only set status after proxy failed.
            remove this proxy from self._pool, self._table[domain],
            and priority queue.

        :param url: get the domain
        :param proxy:
        :param status: fail or success
        """
        domain = urlparse.urlparse(url).netloc
        proxies_table = self._table[domain]
        now = time.time()

        if status == self.FAILED:
            if proxy in proxies_table:
                last_time, count = proxies_table[proxy]
                _count = self._count_rule('set', count)
                if _count >= self.FAIL_THRESHOLD:
                    proxies_table.pop(proxy)
                    # 1. this proxy not available, remove from pool
                    # 2. this proxy avaiable for other sites, not remove
                    self._pool.remove(proxy)

                    if 'priority' in proxies_table:
                        proxies_table['priority'].remove([last_time, count, proxy])
                        heapq.heapify( proxies_table['priority'] )
                else:
                    proxies_table[proxy][1] = _count
                    idx = proxies_table['priority'].index([last_time, count, proxy])
                    proxies_table['priority'][idx][1] = _count

            else: # not execute here now
                proxies_table[proxy] = (now, 1)
        elif status == self.SUCCESS:
            pass


    def get_data_structure(self):
        if self._pool and self._table:
            with open(self.dump_file, 'w') as fd:
                json.dump((list(self._pool), self._table), fd)
        return (list(self._pool), self._table)

