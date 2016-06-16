#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Sharding redis need a hash_id to retrieve its item.
# Save all hash_id in queue redis.
#
# * Queue can save item uniquely, can pop precise number of items,
# but can not count failure times.
# * HashQueue can save item uniquely, can count failure times.
# but can not hscan precese number of items even with count parameter,
# the range is [0, 100]

import time

from redispool import RedisPool
from record import Record


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

        self.batch_size = 5000
        self.conn = RedisPool.instance().queue


    def clear(self):
        """ timehash maybe still have items
        """
        return self.conn.delete(self.key)

    def flush(self):
        self.conn.delete(self.timehash)
        self.conn.delete(self.key)

    def qsize(self):
        return self.conn.scard(self.key)

    def delete(self, *items):
        if items:
            return self.conn.srem(self.key, *items)
        else:
            return 0

    def put(self, *items):
        """ put item(s) into queue """
        if items:
            return self.conn.sadd(self.key, *items)
        else:
            return 0

    def get(self, block=True, timeout=None, interval=0.1):
        """ get item from queue, block if needed

        Usage::

        >>> q.get(block=True)
        >>> q.get(block=True, timeout=3, interval=1)
        >>> # before poping one key, block forever or 3 secnods.

        """
        # 1.queue empty, 2.queue connect time out.
        if block:
            t = 0
            while timeout is None or t < timeout:
                result = self.conn.spop(self.key)
                if not result:
                    t += interval
                    time.sleep(interval)
                else: break
        else:
            result = self.conn.spop(self.key)

        if result:
            self.task_start(result)
        return result


    def task_start(self, result):
        """ save start time in redis hash """
        self.conn.hsetnx(self.timehash, result, time.time())

    def task_done(self, result):
        """ clear start time in redis hash, indicating the task done
            increase successful count in record hash
        """
        return self.conn.hdel(self.timehash, result)

    def clean_task(self):
        """ check task hash for unfinished long running tasks, requeue them.

            Requeue safety:
            `self.timeout` must longer than crawler(worker) job timeout,
            or else `clean_task` add item back to queue, at the same time,
            job finished and removed from `self.timehash`.
        """
        timeout = self.timeout
        if timeout is None:
            self.conn.delete(self.timehash)
            return

        items = []
        time_now = time.time()
        for field, value in self.conn.hgetall(self.timehash).iteritems():
            start_time = float(value)
            if time_now - start_time > timeout:
                items.append(field)

        items, items_tail = items[:self.batch_size], items[self.batch_size:]
        while items:
            print('requeuing {} items(e.g. ... {}) to {}'.format(len(items), items[-10:], self.key))
            pipeline = self.conn.pipeline()
            pipeline.hdel(self.timehash, *items)
            pipeline.sadd(self.key, *items)
            pipeline.execute()
            items, items_tail = items_tail[:self.batch_size], items_tail[self.batch_size:]


    def background_cleaning(self):
        """ If this thread start, without item enqueue in three self.timeout,
            background_cleaning will end.
        """
        ret = self.conn.hsetnx(self.timehash, 'background_cleaning', 1)
        if ret == '0':
            return

        while self.qsize() > 0 or self.conn.hlen(self.timehash) > 1:
            self.clean_task()
            time.sleep(self.timeout)

        self.conn.hset(self.timehash, 'background_cleaning', 0)
        return self.key


    def get_background_cleaning_status(self):
        """ if self.flush, hget will not generate self.timehash key again
        """
        return self.conn.hget(self.timehash, 'background_cleaning')



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

        HashQueue has count on every task of get, failed after 3 times
    """


    def __init__(self, key, priority=1, timeout=180, failure_times=3):
        """
        :param timeout: 如果timeout后，background_cleansing 把任务又加入队列.
                        task_done 来的超时，
                        Record success就会一直增加，甚至超过 Recordtotal
        """
        self.key = key
        self.timehash = '{key}-timehash'.format(key=key)
        self.priority = priority
        self.timeout = timeout
        self.failure_times = failure_times

        self.batch_size = 5000
        self.conn = RedisPool.instance().queue


    def clear(self):
        """ timehash maybe still have items
        """
        return self.conn.delete(self.key)

    def flush(self):
        self.conn.delete(self.timehash)
        self.conn.delete(self.key)

    def qsize(self):
        return self.conn.hlen(self.key)

    def delete(self, *items):
        if items:
            return self.conn.hdel(self.key, *items)
        else:
            return 0

    def put_init(self, *items):
        """ put item(s) into queue """
        if items:
            return self.conn.hmset(self.key, {i:0 for i in items})
        else:
            return 0

    def put(self, *items):
        """ put item(s) into queue

        param *items: (item1, count), (item2, count), ...
        """
        if items:
            return self.conn.hmset(self.key, dict(items))
        else:
            return 0

    def get(self, block=True, timeout=None, interval=0.1):
        """ get item(s) from queue, block if needed

        Usage::

        >>> q.get(block=True) # empty queue will block forever
        >>> q.get(block=True, timeout=5)

        * hscan may return an item multiple times in a full iteration.
        * elements that were not constantly present in the collection during
          a full itertaion, may be returned or not.
        * hscan may return 0 to a few tens of elements.
        * hscan with count=1 may always return empty.
          So need count set to 2 with next_seq iteration.
        * hashes or sorted set encoded as ziplists, all returned in first scan
          call regardless of the count value.

        So the time of re-queue timeout is hard to define. 100 * timeout
        Ensure whether the queue is empty, need get() more times.
        """
        # TODO: queue connect time out.
        cursor = 0
        if block:
            t = 0
            while timeout is None or t < timeout:
                # items is {} object
                next_seq, items = self.conn.hscan(self.key, cursor=cursor, count=2)
                if not items:
                    t += interval
                    time.sleep(interval)
                    cursor = next_seq
                else: break
        else:
            next_seq, items = self.conn.hscan(self.key, cursor=cursor, count=2)

        # SCAN does not provide guarantees about the
        # number of elements returned at every iteration.
        results = []
        if items:
            for field, count in items.iteritems():
                self.task_start(field, count)
                results.append((field, count))
                self.conn.hdel(self.key, field)
        return results


    def task_start(self, result, count):
        """ save start time in redis hash """
        self.conn.hsetnx(self.timehash, result, '{}:{}'.format(time.time(), count))

    def task_done(self, result):
        """ clear start time in redis hash, indicating the task done
            increase successful count in record hash
        """
        return self.conn.hdel(self.timehash, result)

    def clean_task(self):
        """ check task hash for unfinished long running tasks,
            requeue them and add failure count.
            If failure count larger than valid scope,
            add failure count in record hash

        Requeue safety:
            `self.timeout` must longer than crawler(worker) job timeout,
            or else `clean_task` add item back to queue, at the same time,
            job finished and removed from `self.timehash`.
        """
        timeout = self.timeout
        if timeout is None:
            self.conn.delete(self.timehash)
            return

        items = []
        time_now = time.time()
        for field, value in self.conn.hgetall(self.timehash).iteritems():
            if field == 'background_cleaning': continue

            start_time, count = value.rsplit(':', 1)
            start_time = float(start_time)
            if time_now - start_time > timeout:
                count = int(count) + 1
                if count > self.failure_times:
                    Record.instance().increase_failed(self.key)
                    self.conn.hdel(self.timehash, field)
                else:
                    items.append((field, count))

        items, items_tail = items[:self.batch_size], items[self.batch_size:]
        while items:
            print('requeuing {} items(e.g. ... {}) to {}'.format(len(items), items[-10:], self.key))
            pipeline = self.conn.pipeline()
            pipeline.hdel(self.timehash, *[i[0] for i in items])
            pipeline.hmset(self.key, dict(items))
            pipeline.execute()
            items, items_tail = items_tail[:self.batch_size], items_tail[self.batch_size:]


    def background_cleaning(self):
        """ If this thread start, without item enqueue in three self.timeout,
            background_cleaning will end.
        """
        ret = self.conn.hsetnx(self.timehash, 'background_cleaning', 1)
        if ret == '0':
            return

        print('begin clean : ', self.key)
        while self.qsize() > 0 or self.conn.hlen(self.timehash) > 1:
            self.clean_task()
            time.sleep(60) # no need self.timeout long

        print('finish clean : ', self.key)
        self.conn.hset(self.timehash, 'background_cleaning', 0)
        return self.key


    def get_background_cleaning_status(self):
        """ if self.flush, hget will not generate self.timehash key again
        """
        return self.conn.hget(self.timehash, 'background_cleaning')
