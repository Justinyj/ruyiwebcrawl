#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json

from rediscluster.record import Record
from rediscluster.queues import HashQueue
from rediscluster.thinredis import ThinHash
from schedule import Schedule

def post_job(self, batch_id, method, gap, js, urls, machine_num):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.
    """
    total_count = len(urls)

    parameter = '{method}:{gap}:{js}:{data}'.format(
            method=method,
            gap=gap,
            js=1 if js else 0,
            data='')

    Record.instance().begin(batch_id, parameter, total_count)
    queue = HashQueue(batch_id, priority=2, timeout=90, failure_times=3)

    thinhash = ThinHash(batch_id, total_count)
    for url in urls:
        if isinstance(url, unicode):
            url = url.encode('utf-8')
        field = int(hashlib.sha1(url).hexdigest(), 16)
        thinhash.hset(field, url)

        queue.put_init(field)

    schedule = Schedule(machine_num, tag=batch_id.split('-', 1)[0])
    schedule.run()


def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Call crawler with arguments')
    parser.add_argument('--batch', '-b', type=str, help='batch_id')
    parser.add_argument('--method', '-m', type=str, help='get or post')
    parser.add_argument('--gap', '-g', type=int, help='sleep between two crawl')
    parser.add_argument('--js', '-j', type=bool, help='use js or not')
    parser.add_argument('--file', '-f', type=str, help='use js or not')
    parser.add_argument('--instances', '-i', type=int, help='open instance number')
    option = parser.parse_args()

    urls = load_urls(option.file)
    post_job(option.batch, option.method, option.method, option.gap, urls, option.instances)

if __name__ == '__main__':
    main()

