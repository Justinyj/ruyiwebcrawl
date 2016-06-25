#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import hashlib
import json
import gevent

from rediscluster.redismanager import RedisManager
from settings import RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS


MANAGER = RedisManager(RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS)

def post_job(batch_id, method, gap, js, urls, total_count=None, priority=1, queue_timeout=10, failure_times=3, start_delay=0):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.

    :param queue_timeout: turn to several times larger of download timeout.
    """
    total_count = len(urls) if len(urls) > 0 else total_count

    parameter = '{method}:{gap}:{js}:{timeout}:'.format(
            method=method,
            gap=gap,
            js=1 if js else 0,
            timeout=queue_timeout)

    queue_timeout *= 20 # magic number because of the queue.get
    queue_dict = MANAGER.init_distributed_queue(batch_id,
                                                parameter,
                                                total_count,
                                                priority,
                                                timeout=queue_timeout,
                                                failure_times=failure_times)
    MANAGER.put_urls_enqueue(batch_id, urls)

    return gevent.spawn_later(start_delay, queue_dict['queue'].background_cleaning)


def delete_distributed_queue(greenlet):
    """ In this callback, the greenlet.value is batch_id
        this will be called after gevent.joinall
    """
    return MANAGER.delete_queue(greenlet.value)


def main():
    pass

if __name__ == '__main__':
    main()

