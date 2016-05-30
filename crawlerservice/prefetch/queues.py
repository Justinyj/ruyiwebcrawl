#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# All items under one hashkey, so we can test whether the Queue is empty.
# That is to say, items can not be distributed in sharding redis.

import re
import time
import redis

from settings import QUEUE_REDIS

host, port, db = re.compile('(.*):(\d+)/(\d+)').search(QUEUE_REDIS).groups()
conn = redis.Redis(host=host, port=int(port), db=int(db))

class Queue(object):
    """ an unordered queue wrapper for redis, provides Queue.Queue like methods

    Usage::

    >>> q = Queue('queue-name', priority=1)
    >>> q.put(1, 2, 3)
    >>> q.get(block=False)
    2

    >>> # do something with item id 2

    when an item is poped, we also updated poping timestamp in a ``hash``
    upon task finish, we should call ``task_done`` to remove that timestamp

    >>> q.task_done(2)

    if a task isn't finished normally, ``task_done`` will not be executed, 
    thus we can findout items spent too much time in that hash, and have 
    them requeued in the queue

    see ``Queue.clean_tasks`` method for details
    """
    def __init__(self, key, priority=1, timeout=90):
        self.key = key
        self.timehash = '{key}-timehash'.format(key=key)
        self.priority = priority
        self.timeout = timeout

    def clear(self):
        return conn.delete(self.key)

    def qsize(self):
        return conn.scard(self.key)

    def delete(self, *items):
        if items:
            return conn.srem(self.key, *items)
        else:
            return 0

    def put(self, *items):
        """ put item(s) into queue """
        if items:
            return conn.sadd(self.key, *items)
        else:
            return 0

    def get(self, block=True, timeout=None):
        """ get item from queue, block if needed

        Usage::

        >>> q.get(block=True)
        >>> q.get(block=True, timeout=5)
        >>> # before poping one key, block forever or 5 secnods.

        """
        # TODO: 1.queue empty, 2.queue connect time out.
        if block:
            t = 0
            while timeout is None or t < timeout:
                result = conn.spop(self.key)
                if not result:
                    t += 0.1
                    time.sleep(0.1)
                else: break
        else:
            result = conn.spop(self.key)

        if result:
            self.task_start(result)
        return result


    def task_start(self, result):
        """ save start time in redis hash """
        conn.hsetnx(self.timehash, result, time.time())

    def task_done(self, result):
        """ clear start time in redis hash, indicating the task done """
        return conn.hdel(self.timehash, result)

    def clean_task(self):
        """ check task hash for unfinished long running tasks, requeue them.

            Requeue safety:
            `self.timeout` must longer than crawler(worker) job timeout,
            or else `clean_task` add item back to queue, at the same time,
            job finished and removed from `self.timehash`.
        """
        timeout = self.timeout
        if timeout is None:
            conn.delete(self.timehash)
            return

        BATCH = 5000
        items = []
        time_now = time.time()
        for field, value in conn.hgetall(self.timehash).iteritems():
            start_time = float(value)
            if time_now - start_time > timeout:
                items.append(field)

        items, items_tail = items[:BATCH], items[BATCH:]
        while items:
            print('requeuing {} items(e.g. ... {}) to {}'.format(len(items), items[-10:], self.key))
            pipeline = conn.pipeline()
            pipeline.hdel(self.timehash, *items)
            pipeline.sadd(self.key, *items)
            pipeline.execute()
            items, items_tail = items_tail[:BATCH], items_tail[BATCH:]

    def background_cleaning(self):
        while True:
            self.clean_task()
            time.sleep(60)
        

def poll(queues, timeout=None):
    """ poll item from queues (order by priority) 

    :param queues: instances of queues, can not be empty
    :param timeout: how much time should be used to wait for results, `None` means not limited
    :returns: a tuple of (queue, result), the respective queue and result
    """
    queues = sorted(queues, key=lambda x: x.priority, reverse=True)
    t = 0
    while timeout is None or t < timeout:
        for q in queues:
            result = q.get(block=False)
            if result is not None:
                return q, result
        t += 0.5
        time.sleep(0.5)



class HashQueue(object):
    """ The Queue volume is very large, so can not use ziplists compression.
        Then HashQueue is unnecessary.
    """
    def __init__(self, key, priority=1, timeout=90):
        self.key = key
        self.timehash = '{key}-timehash'.format(key=key)
        self.priority = priority
        self.timeout = timeout

    def clear(self):
        return conn.delete(self.key)

    def qsize(self):
        return conn.hlen(self.key)

    def delete(self, *items):
        if items:
            return conn.hdel(self.key, *items)
        else:
            return 0

    def put(self, *items):
        """ put item(s) into queue """
        if items:
            return conn.hmset(self.key, {i:0 for i in items})
        else:
            return 0

    def get(self, block=True, timeout=None):
        """ get item(s) from queue, block if needed

        Usage::

        >>> q.get(block=True) # empty queue will block forever
        >>> q.get(block=True, timeout=5)
        """
        # TODO: 1.queue empty, 2.queue connect time out.
        if block:
            t = 0
            while timeout is None or t < timeout:
                # items is {} object
                next_seq, items = conn.hscan(self.key, cursor=0, count=1)
                if not items:
                    t += 0.1
                    time.sleep(0.1)
                else: break
        else:
            next_seq, items = conn.hscan(self.key, cursor=0, count=1)

        # SCAN does not provide guarantees about the
        # number of elements returned at every iteration.
        result = []
        if items:
            for item, _ in items.iteritems():
                self.task_start(item)
                result.append(item)
        return result


    def task_start(self, result):
        """ save start time in redis hash """
        conn.hsetnx(self.timehash, result, time.time())

    def task_done(self, result):
        """ clear start time in redis hash, indicating the task done """
        return conn.hdel(self.timehash, result)

    def clean_task(self):
        """ check task hash for unfinished long running tasks, requeue them.

            Requeue safety:
            `self.timeout` must longer than crawler(worker) job timeout,
            or else `clean_task` add item back to queue, at the same time,
            job finished and removed from `self.timehash`.
        """
        timeout = self.timeout
        if timeout is None:
            conn.delete(self.timehash)
            return

        BATCH = 5000
        items = []
        time_now = time.time()
        for field, value in conn.hgetall(self.timehash).iteritems():
            start_time = float(value)
            if time_now - start_time > timeout:
                items.append(field)

        items, items_tail = items[:BATCH], items[BATCH:]
        while items:
            print('requeuing {} items(e.g. ... {}) to {}'.format(len(items), items[-10:], self.key))
            pipeline = conn.pipeline()
            pipeline.hdel(self.timehash, *items)
            pipeline.hmset(self.key, {i:0 for i in items})
            pipeline.execute()
            items, items_tail = items_tail[:BATCH], items_tail[BATCH:]

    def background_cleaning(self):
        while True:
            self.clean_task()
            time.sleep(60)


task_queue = Queue('task-queue', priority=2, timeout=90)
failed_queue = Queue('failed-queue', priority=1, timeout=90)
