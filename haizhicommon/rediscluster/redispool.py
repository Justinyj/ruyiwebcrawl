#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import redis
import contextlib


class RedisPool(object):
    """ `StrictRedis` has its default redis pool,
        read the source code about `execute_command`
        https://redis-py.readthedocs.io/en/latest/_modules/redis/client.html

    Usage::

    >>> conn = RedisPool.instance().queue
    """
    def __init__(self, record_redis, queue_redis, cache_redis, poolsize=5):
        """ password is None means no password
        """
        regx_redis = re.compile('redis://(.+):(\d+)/(\d+)/?(.+)?')

        host, port, db, password = regx_redis.search(record_redis).groups()
        self.record = redis.StrictRedis(host=host, port=int(port), db=int(db), password=password)

        host, port, db, password = regx_redis.search(queue_redis).groups()
        self.queue = redis.StrictRedis(host=host, port=int(port), db=int(db), password=password)

        self.caches = []
        for one_cache_redis in cache_redis:
            host, port, db, password = regx_redis.search(one_cache_redis).groups()
            self.caches.append( redis.StrictRedis(host=host, port=int(port), db=int(db), password=password, max_connections=poolsize) )


    @classmethod
    def instance(cls, *args):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls(*args)
        return cls._instance

