#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thin Redis only support hashable items key(integer), then they can
# be distributed to different buckets by modulo result.
# python build-in hash or int(hashlib.sha1(str).hexdigest(), 16)

""" A simplified and thin set/hash for redis

A "real set/hash" in redis has too much overhead (~10x)

This is a simplified version of set/hash, 
    * only integer/biginteger values supported
    * for set, only ``contains``, ``add`` and  ``delete`` is supported

By doing this simplification, we are able to take advantage of ``redis``'s 
zipentry optimization. Thus the size of set/hash can be reduced to
1/4 ~ 1/3 of the original size.

The concept comes from `this stackoverflow question 
<http://stackoverflow.com/questions/10004565/redis-10x-more-memory-usage-than-data/10008222#10008222>`_
"""

import redis
import hashlib

from shardredis import ShardRedis
from redispool import RedisPool

class ThinSet(object):
    """ counter key: string
        buckets key: set, {bucket1, bucket2, ...}
        bucket1 key: set
    """
    def __init__(self, key, totalcount, connection=None):
        """ connection can be redis.Redis()
        """
        self.key = key
        self.total = totalcount
        self.modulo = max(1, totalcount // 200)
        self.counterkey = 'thinset_{}_count'.format(key)
        self.bucketskey = 'thinset_{}_buckets'.format(key)
        if connection is not None:
            self.conn = connection
        else:
            self.conn = ShardRedis(conns=RedisPool.instance().caches)

    def _get_bucket(self, item):
        return 'thinset_{}_{}'.format(self.key, int(item) % self.modulo)


    def count(self):
        r = self.conn.get(self.counterkey)
        return 0 if r is None else int(r)

    def recount(self):
        p = self.conn.pipeline(transaction=False)
        for i in range(self.modulo):
            bucket = 'thinset_{}_{}'.format(self.key, i)
            p.scard(bucket)
        count = sum(p.execute())
        return self.conn.set(self.counterkey, count)

    def add(self, *items):
        if len(items) == 0:
            return
           
        p = self.conn.pipeline(transaction=False)

        buckets = set()
        for item in items:
            bucket = self._get_bucket(item)
            buckets.add(bucket)
            p.sadd(bucket, item)

        added = sum(p.execute())

        if added:
            self.conn.incr(self.counterkey, added)
            self.conn.sadd(self.bucketskey, *list(buckets))
    

    def delete(self, *items):
        if len(items) == 0:
            return
            
        p = self.conn.pipeline(transaction=False) 

        for item in items: 
            bucket = self._get_bucket(item)
            p.srem(bucket, item)

        deleted = sum(p.execute())

        if deleted:
            self.conn.decr(self.counterkey, deleted)


    def contains(self, *items):
        """ order preserving contains, works only for shardredis """
        if not items:
            return []

        p = self.conn.pipeline(transaction=False)
    
        if not hasattr(self.conn, 'ring'):
            for item in items:
                bucket = self._get_bucket(item)
                p.sismember(bucket, item)
            return p.execute()
        else:
            pointers = {}
            for i, item in enumerate(items):
                bucket = self._get_bucket(item)
                index = self.conn.ring.get_node(bucket)
                if index not in pointers:
                    pointers[index] = []
                pointers[index].append(i)
                p.sismember(bucket, item)

            orders = []
            for index in range(len(self.conn.conns)):
                if index in pointers:
                    orders.extend(pointers[index])
                
            values = p.execute()
            _, values = zip(*sorted(zip(orders, values)))
            return values

    def smembers(self):
        buckets = self.conn.smembers(self.bucketskey)

        p = self.conn.pipeline(transaction=False)
        for bucket in buckets:
            p.smembers(bucket)
        r = set()
        for s in p.execute():
            r.update(s)

        return r


class ThinHash(object):
    """ Data Structure:
            counter key: string
            buckets key: set, {bucket1, bucket2, ...}
            bucket1 key: hashmap

        Usage:

        >>> conn = ShardRedis(conns=[Redis(db=1), Redis(db=2)])
        >>> thinhash = ThinHash('batch_id', 10000, conn)
        >>> field = int(hashlib.sha1('field1').hexdigest(), 16)
        >>> thinhash.hset(field, 'value1')
        None

        >>> thinhash.hget(field)
        'value1'

    """
    def __init__(self, key, totalcount, connection=None):
        """ connection can be redis.Redis()
        """
        self.key = key
        self.counterkey = 'thinhash_{}_count'.format(key)
        self.bucketskey = 'thinhash_{}_buckets'.format(key)
        self.modulo = max(1, totalcount // 200) # ensure not zero
        if connection is not None:
            self.conn = connection
        else:
            self.conn = ShardRedis(conns=RedisPool.instance().caches)

    def _get_bucket(self, field):
        return 'thinhash_{}_{}'.format(self.key, int(field) % self.modulo)

    def delete(self):
        p = self.conn.pipeline(transaction=False)
        for i in range(self.modulo):
            bucket = 'thinhash_{}_{}'.format(self.key, i)
            p.delete(bucket)
        p.delete(self.counterkey)
        p.delete(self.bucketskey)
        p.execute()

    def count(self):
        r = self.conn.get(self.counterkey)
        return 0 if r is None else int(r)

    def recount(self):
        p = self.conn.pipeline(transaction=False)
        for i in range(self.modulo):
            bucket = 'thinhash_{}_{}'.format(self.key, i)
            p.hlen(bucket) 
        count = sum(p.execute())
        return self.conn.set(self.counterkey, count)

    def hset(self, field, value):
        bucket = self._get_bucket(field)
        r = self.conn.hset(bucket, field, value) 
        self.conn.sadd(self.bucketskey, bucket)
        if r:
            self.conn.incr(self.counterkey, r)

    def hdel(self, field):
        bucket = self._get_bucket(field)
        deleted = self.conn.hdel(bucket, field) 
        if deleted:
            self.conn.decr(self.counterkey, deleted)

    def hget(self, field):
        bucket = self._get_bucket(field)
        return self.conn.hget(bucket, field)
       
    def hmset(self, *args):
        if len(args) == 0:
            return
        elif len(args) % 2 != 0:
            raise ValueError("hmset only accept even arguments")

        p = self.conn.pipeline(transaction=False)
        buckets = set()
        for i in range(len(args)/2):
            field, value = args[i*2], args[i*2+1]
            bucket = self._get_bucket(field)
            buckets.add(bucket)
            p.hset(bucket, field, value)

        added = sum(p.execute())
        if added:
            self.conn.incr(self.counterkey, added)
            self.conn.sadd(self.bucketskey, *buckets)

    def hmget(self, *fields):
        """ order preserving hmget, works only for shardredis """
        if len(fields) == 0:
            return

        p = self.conn.pipeline(transaction=False)
        if not hasattr(self.conn, 'ring'):
            for field in fields:
                bucket = self._get_bucket(field)
                p.hget(bucket, int(field))
            return p.execute()
        else:
            pointers = {}
            for i, field in enumerate(fields):
                bucket = self._get_bucket(field)
                index = self.conn.ring.get_node(bucket)
                if index not in pointers:
                    pointers[index] = []
                pointers[index].append(i)
                p.hget(bucket, int(field))
            orders = []
            for index in range(len(self.conn.conns)):
                if index in pointers:
                    orders.extend(pointers[index])
                
            values = p.execute()
            _, values = zip(*sorted(zip(orders, values)))
            return values

    def hgetall(self):
        buckets = self.conn.smembers(self.bucketskey)
        p = self.conn.pipeline(transaction=False)
        for bucket in buckets:
            p.hgetall(bucket)
        r = {}
        for d in p.execute():
            r.update(d)
        return r

    def hkeys(self):
        buckets = self.conn.smembers(self.bucketskey)
        p = self.conn.pipeline(transaction=False)
        for bucket in buckets:
            p.hkeys(bucket)
        r = set()
        for s in p.execute():
            r.update(s)
        return r


class CappedSortedSet(object):
    """ Capped sorted set for redis
    After adding new element to zset, if elements number exceed capped,
    delete from one end of the small element.
    
    implemented using redis's lua scripting support, need redis 2.6+
    """
    # lua script operation for a capped sorted set
    script = '\n'.join([
            'redis.call("ZADD", KEYS[1], ARGV[2]+0, ARGV[1])',
            'local n = redis.call("ZCARD", KEYS[1])',
            'if n > ARGV[3]+0 then redis.call("ZREMRANGEBYRANK", KEYS[1], 0, n-ARGV[3]-1) end',
        ])
    sha1 = hashlib.sha1(script).hexdigest()
    inited = False

    def __init__(self, key, cap, conn, **kwargs):
        self.key = key
        self.cap = cap
        self.conn = conn
        self.kwargs = kwargs
        if not CappedSortedSet.inited:
            self.conn.script_load(self.script)
            CappedSortedSet.inited = True
    
    def zadd(self, member, score, **kwargs):
        kwargs.update(self.kwargs)
        self.conn.evalsha(self.sha1, 1, self.key, member, score, self.cap, **kwargs)

    def zrange(self, start, end, **kwargs):
        kwargs.update(self.kwargs)
        return self.conn.zrange(self.key, start, end, **kwargs)
