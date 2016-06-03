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
    def work(self):
        print(self.pool)

    def get_task_queue(self):
        queues = []
        keys = Record.instance().get_unfinished_batch()
        for key in keys:
            queue = HashQueue(key, priority=2, timeout=90, failure_times=3)
            return queue

    def _check_empty_queue(self, queue):
        """ after 3 times of get, result is empty
        """
        for i in range(3):
            result = queue.get(block=True, timeout=3, interval=1)
            if result != []:
                return False
        return True

    def delete_queue_check(self, queue):
        status = queue.get_background_cleaning_status()
        if status != '0':
            return False
        ret = Record.instance().is_finished()
        if ret is True:
            return False
        ret = self._check_empty_queue()
        if ret is False:
            return False
        return True
    def run(self):
        queue = self.get_task_queue()
        status = queue.get_background_cleaning_status()
        if status is None: # not running yet
            gevent.spawn(queue.background_cleaning)
            # TODO start crawling
        elif status == '1': # running
            pass
        elif status == '0': # finished job
            ret = self.delete_queue_check(queue)
            if ret is True:
                # caution!! atom operation
                Record.instance().end()
                queue.flush()
                ThinHash.delete()
                
            # delete queue and distribute queue






def producer(poolsize):
    ReQueueWorker().work()
    while True:
        time.sleep(60)

def consumer(poolsize, backhaul):
    GetWorker(poolsize, backhaul).work()

print( GetWorker(3).pool )

