#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from rediscluster.record import Record
from rediscluster.queues import HashQueue
from rediscluster.thinredis import ThinHash
from rediscluster.redispool import RedisPool

from operator import itemgetter
import hashlib

class RedisManager(object):

    def __init__(self, record_redis, queue_redis, cache_redis, poolsize=5):
        """ Caution!! need init RedisPool here, ThinHash, HashQueue, Record can call
            this RedisPool single instance later.
        """
        RedisPool.instance(record_redis, queue_redis, cache_redis, poolsize)
        self.cache = {}


    def init_distributed_queue(self,
                               batch_id,
                               parameter,
                               total_count,
                               priority=1,
                               timeout=180,
                               failure_times=3):
        """ init distributed queue for master side

        param total_count: can be a predetermined number larger than real total_count
        """
        # keep the step order
        Record.instance().begin(batch_id, parameter, total_count, priority)
        thinhash = ThinHash(batch_id, total_count)
        queue = HashQueue(batch_id,
                          priority=priority,
                          timeout=timeout,
                          failure_times=failure_times)

        self.set_distributed_queue(batch_id, queue, thinhash, priority, True)
        return self.cache[batch_id]


    def worker_init_distributed_queue(self, batch_id, total_count):
        """ init distributed queue for worker side
        """
        priority = int( Record.instance().get_priority(batch_id) )
        thinhash = ThinHash(batch_id, total_count)
        queue = HashQueue(batch_id, priority=priority)
        self.set_distributed_queue(batch_id, queue, thinhash, priority, True)
        return self.cache[batch_id]

    def get_queue_with_priority(self):
        """ low priority queu may generated by high priority queue,
            so if worker get from low priority first,
            it can be always empty, and deleted by master schedule.
        """
        result = []
        for batch_id, queue_dict in self.cache.iteritems():
            result.append((batch_id, queue_dict, queue_dict['priority']))

        for i in sorted(result, key=itemgetter(2), reverse=True):
            yield (i[0], i[1])

    def set_distributed_queue(self, batch_id, queue, thinhash, priority, refresh=True):
        if not (queue and thinhash):
            return
        if refresh:
            self.cache[batch_id] = {'queue': queue, 'thinhash': thinhash, 'priority': priority}
        elif batch_id not in self.cache:
            self.cache[batch_id] = {'queue': queue, 'thinhash': thinhash, 'priority': priority}
        else:
            pass


    def get_distributed_queue(self, batch_id):
        if batch_id not in self.cache:
            return
        return self.cache[batch_id]


    def put_url_enqueue(self, batch_id, url):
        if batch_id not in self.cache:
            return False

        if isinstance(url, unicode):
            url = url.encode('utf-8')
        field = int(hashlib.sha1(url).hexdigest(), 16)
        # keep the order
        self.cache[batch_id]['thinhash'].hset(field, url)
        self.cache[batch_id]['queue'].put_init(field)
        return True


    def put_urls_enqueue(self, batch_id, urls):
        if batch_id not in self.cache:
            return False
        if not urls:
            return False

        thinhash_mset = []
        queue_mset = []
        for url in urls:
            if isinstance(url, unicode):
                url = url.encode('utf-8')
            field = int(hashlib.sha1(url).hexdigest(), 16)
            thinhash_mset.append(field)
            thinhash_mset.append(url)
            queue_mset.append((field, 0))

        self.cache[batch_id]['thinhash'].hmset(*thinhash_mset)
        self.cache[batch_id]['queue'].put(*queue_mset)
        return True

    def get_status(self, batch_id):
        """
        0: init
        1: running
        2: finished
        """
        pass

    def delete_queue(self, batch_id):
        distributed = self.get_distributed_queue(batch_id)
        if distributed is None:
            return
        if distributed['queue'].get_background_cleaning_status() != '0':
            return


        if Record.instance().if_not_finish_set(batch_id) == 1:
            distributed['thinhash'].delete()
            distributed['queue'].flush()
            self.cache.pop(batch_id)
            return True


    def __check_empty_queue(self, queue):
        """ after 5 times of get, result is empty
            for HashQueue need more times check cause it may return 0 element
        """
        results = queue.get(block=True, timeout=5, interval=1)
        return False if results != [] else True


