#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json

from rediscluster.record import Record
from rediscluster.queues import HashQueue
from rediscluster.thinredis import ThinHash

def post_job(self, batch_id, method, gap, js, header, urls):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.
    """
    total_count = len(urls)

    parameter = '{method}:{gap}:{js}:{headers}:{data}'.format(
            method=method,
            gap=gap,
            js=1 if js else 0,
            header=json.dumps(header) if header else '',
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

def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']

if __name__ == '__main__':
    urls = load_urls('prefetch.txt')
    post_job('qichacha_fetch_20160604', 'get', 5, False, {}, urls)

