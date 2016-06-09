#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json

from rediscluster.redismanager import RedisManager
from schedule import Schedule

manager = RedisManager()

def post_job(batch_id, method, gap, js, urls, total_count=None):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.
    """
    total_count = len(urls) if len(urls) > 0 else total_count

    parameter = '{method}:{gap}:{js}:'.format(
            method=method,
            gap=gap,
            js=1 if js else 0)

    manager.init_distributed_queue(batch_id, parameter, total_count)
    manager.put_urls_enqueue(batch_id, urls)


def start_up_ec2(machine_num, batch_tag):
    schedule = Schedule(machine_num, tag=batch_tag)
    schedule.run()

def main():
    pass

if __name__ == '__main__':
    main()

