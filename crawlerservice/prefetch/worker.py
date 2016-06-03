#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from gevent import monkey; monkey.patch_all()
from queues import HashQueue

import gevent.pool

class Worker(object):
    """ General worker
    """
    def __init__(self, poolsize=100):
        self.pool = gevent.pool.Pool(poolsize)

    def work(self):
        raise NotImplementedError('This method should implemented by subclasses')

class ReQueueWorker(Worker):
    """ ReQueue Timeouted Jobs
    """
    def work(self):
        """ if gevent.joinall([ ]), will waiting for the endless background_cleaning,
            then we need have a endless loop after this function work().
        """
        [gevent.spawn(queue.background_cleaning) for queue in [task_queue]]


class GetWorker(Worker):
    def __init__(self, poolsize=100):
        super(GetWorker, self).__init__(poolsize)
        self.queues = [i for i in self._get_task_queue()]

    def _get_task_queue(self):
        keys = Record.instance().get_unfinished_batch()
        for key in keys:
            yield HashQueue(key, priority=2, timeout=90, failure_times=3)

    def work(self):
        print(self.pool)

    def _check_empty_queue(self, queue):
        """ after 3 times of get, result is empty
        """
        for i in range(3):
            result = queue.get(block=True, timeout=3, interval=1)
            if result != []:
                return False
        return True

    def delete_queue_check(self, queue):
        ret = self._check_empty_queue(queue)
        if ret is False:
            return False
        ret = Record.instance().is_finished(queue.key)
        if ret is True:
            return False
        status = queue.get_background_cleaning_status()
        if status != '0':
            return False
        return True

    def run(self):
        """ end, background_cleansing, status:
            0,   None,                 begin
            0,   1,                    begin cleansing
            0,   0,                    finish cleansing
         time,   0,                    begin delete
         time,   None,                 finish delete
            0,   0,                    finish cleansing with exception
        """
        queue = self.queues[0]
        background = queue.get_background_cleaning_status()
        if Record.instance().is_finished(queue.key) is True:
            return

        if background is None:
            gevent.spawn(queue.background_cleaning)
            # start crawling
        elif background == '1':
            # start crawling
            pass
        elif background == '0':
            ret = self.delete_queue_check(queue)
            if ret is True:
                # caution! atom operation
                try:
                    Record.instance().end(queue.key)
                    total_count = int( Record.instance().get_total_number() )
                    thinhash = ThinHash(batch_id, total_count)
                    thinhash.delete()
                    queue.flush()
                except:
                    Record.instance().from_end_rollback(queue.key)






def producer(poolsize):
    ReQueueWorker().work()
    while True:
        time.sleep(60)

def consumer(poolsize, backhaul):
    GetWorker(poolsize, backhaul).work()

print( GetWorker(3).pool )

