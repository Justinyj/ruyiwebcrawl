#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import gevent

from rediscluster.redismanager import RedisManager
from awscrawler import post_job
from schedule import Schedule
from invoker.zhidao_constent import BATCH_ID, HEADER


manager = RedisManager()
gcounter = 0

def patch_greenlet(func):
    def inner(*args, **kwargs):
        return gevent.spawn(func, *args, **kwargs)
    return inner

def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']


@patch_greenlet
def delete_distributed_queue(greenlet):
    """ In this callback, the greenlet.value is batch_id
        this will be called after run_zhidao.gevent.joinall
    """
    global manager
    global gcounter
    ret = manager.delete_queue(greenlet.value)
    if ret is True:
        pass
    gcounter += 1


def run_zhidao():
    global manager

    filename = 'useful_zhidao_urls.txt'
    urls = load_urls(filename)

    gtasks = []
    t1 = post_job(BATCH_ID['question'], manager, 'get', 3, False, urls, queue_timeout=100*10)
    t1.rawlink(delete_distributed_queue)
    gtasks.append(t1)
    t2 = post_job(BATCH_ID['answer'], manager, 'get', 3, False, [], len(urls) * 3, queue_timeout=100*10, delay=60)
    t2.rawlink(delete_distributed_queue)
    gtasks.append(t1)

    schedule = Schedule(3, tag=BATCH_ID['question'].split('-', 1)[0], backoff_timeout=100*10/2**3)
    t3 = gevent.spawn(schedule.run_forever)

    gevent.joinall(gtasks)
    gevent.kill(t3, block=True)


    print('wait queue finish monitoring')
    import time
    time.sleep(240)
    schedule.stop_all_instances()

if __name__ == '__main__':
    run_zhidao()

