#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import gevent

from rediscluster.redismanager import RedisManager
from awscrawler import post_job
from schedule import Schedule


BATCH_ID = {
    'question': 'zhidao-question-20160606',
    'answer': 'zhidao-answer-20160606',
    'json': 'zhidao-json-20160606',
    'result': 'zhidao-result-20160606'
}

HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1'
}

manager = RedisManager()
gcounter = 0

def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']

def delete_distributed_queue(greenlet):
    """ In this callback, the return value is batch_id
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

    tasks = []
    t1 = post_job(BATCH_ID['question'], manager, 'get', 3, False, urls)
    t1.rawlink(delete_distributed_queue)
    tasks.append(t1)
    t2 = post_job(BATCH_ID['answer'], manager, 'get', 3, False, [], len(urls) * 3, delay=60)
    t2.rawlink(delete_distributed_queue)
    tasks.append(t1)

    schedule = Schedule(9, tag=BATCH_ID['question'].split('-', 1)[0])
    t3 = gevent.spawn(schedule.run_forever)

    gevent.joinall(tasks)
    gevent.kill(t3, block=True)

    schedule.stop_all_instances()

if __name__ == '__main__':
    run_zhidao()

