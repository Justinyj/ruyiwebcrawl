#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import redis
import contextlib

from settings import RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS

class RedisPool(object):
    """ `StrictRedis` has its default redis pool,
        read the source code about `execute_command`
        https://redis-py.readthedocs.io/en/latest/_modules/redis/client.html

    Usage::

    >>> conn = RedisPool.instance().queue.get_connection(None)
    >>> RedisPool.instance().queue.release(conn)
    """
    def __init__(self, pool_size=5):
        regx_redis = re.compile('(.+):(\d+)/(\d+)')

        host, port, db = regx_redis.search(RECORD_REDIS).groups()
        self.record = redis.ConnectionPool(host=host, port=int(port), db=int(db), max_connections=pool_size)

        host, port, db = regx_redis.search(QUEUE_REDIS).groups()
        self.queue = redis.ConnectionPool(host=host, port=int(port), db=int(db), max_connections=pool_size)

        self.caches = []
        for cache_redis in CACHE_REDIS:
            host, port, db = regx_redis.search(cache_redis).groups()
            self.caches.append( redis.StrictRedis(host=host, port=int(port), db=int(db), max_connections=pool_size) )


    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls()
        return cls._instance


@contextlib.contextmanager
def redis_conn(config):
    """
    Usage::

    >>> with redis_conn('queue') as conn:
    >>> ... 
    """
    pool = getattr(RedisPool.instance(), config)
    conn = pool.get_connection(None)
    yield conn
    pool.release(conn)

