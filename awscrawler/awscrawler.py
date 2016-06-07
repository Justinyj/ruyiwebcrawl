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

    init_distribute_queue(batch_id, parameter, total_count)

    schedule = Schedule(machine_num, tag=batch_id.split('-', 1)[0])
    schedule.run()


def init_distribute_queue(batch_id, parameter, total_count):
    # total_count can be a predetermined number larger than the real total_cout
    # TODO dnynmic add url to queue

    Record.instance().begin(batch_id, parameter, total_count)
    queue = HashQueue(batch_id, priority=2, timeout=90, failure_times=3)

    thinhash = ThinHash(batch_id, total_count)
    for url in urls:
        if isinstance(url, unicode):
            url = url.encode('utf-8')
        field = int(hashlib.sha1(url).hexdigest(), 16)
        thinhash.hset(field, url)

        queue.put_init(field)


def main():
    pass

if __name__ == '__main__':
    main()

