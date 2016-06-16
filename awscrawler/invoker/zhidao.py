#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import gevent
import time

from awscrawler import post_job, delete_distributed_queue
from schedule import Schedule
from invoker.zhidao_constant import BATCH_ID


def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']


def run_zhidao():
    """
        第二个queue开始后，第一个queue还没有跑worker，并把结果塞入第二个queue，第二个queue就end了。
    """

    filename = '/home/admin/split_zhidao_ak'
#    filename = 'useful_zhidao_urls.txt'
    urls = load_urls(filename)

    tasks = []
    t1 = post_job(BATCH_ID['question'], 'get', 3, False, urls, priority=2, queue_timeout=100*10)
    tasks.append(t1)

    t2 = post_job(BATCH_ID['answer'], 'get', 3, False, [], len(urls) * 3, priority=1, queue_timeout=100*10, start_delay=180) # delay is 128 once, wait for question to generate answer
    tasks.append(t2)

    schedule = Schedule(30, tag=BATCH_ID['question'].split('-', 1)[0], backoff_timeout=100*10/2**3)
    print('finish start instances initially')

    t3 = gevent.spawn(schedule.run_forever)

    gevent.joinall(tasks)

    print('waiting for delete queue')
    for greenlet in tasks:
        ret = delete_distributed_queue(greenlet)
        print('{} return of delete {}'.format(ret, greenlet.value))

    gevent.killall([t3], block=True)
    schedule.stop_all_instances()


if __name__ == '__main__':
    run_zhidao()

