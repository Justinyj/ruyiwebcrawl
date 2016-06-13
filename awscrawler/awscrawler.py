#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import hashlib
import json
import gevent

from rediscluster.redismanager import RedisManager


MANAGER = RedisManager()

def post_job(batch_id, method, gap, js, urls, total_count=None, priority=1, queue_timeout=180, failure_times=3, start_delay=0):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.
    """
    total_count = len(urls) if len(urls) > 0 else total_count

    parameter = '{method}:{gap}:{js}:'.format(
            method=method,
            gap=gap,
            js=1 if js else 0)

    queue_dict = MANAGER.init_distributed_queue(batch_id,
                                                parameter,
                                                total_count,
                                                priority,
                                                timeout=queue_timeout,
                                                failure_times=failure_times)
    MANAGER.put_urls_enqueue(batch_id, urls)

    return gevent.spawn_later(start_delay, queue_dict['queue'].background_cleaning)


def patch_greenlet(func):
    def inner(*args, **kwargs):
        return gevent.spawn(func, *args, **kwargs)
    return inner


@patch_greenlet
def delete_distributed_queue(greenlet):
    """ In this callback, the greenlet.value is batch_id
        this will be called after gevent.joinall
    """
    ret = MANAGER.delete_queue(greenlet.value)
    if ret is True:
        pass

def main():
    pass

if __name__ == '__main__':
    main()

