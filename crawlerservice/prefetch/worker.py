#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from gevent import monkey; monkey.patch_all()
from queues import prefetch_urls_queue 

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
        [gevent.spawn(queue.background_cleaning) for queue in [prefetch_urls_queue]]


def producer(poolsize):
    PutWorker(poolsize).work()
    ReQueueWorker().work()
    while True:
        time.sleep(60)

def consumer(poolsize, backhaul):
    GetWorker(poolsize, backhaul).work()

