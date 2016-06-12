#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib
import json

from schedule import Schedule


def post_job(batch_id, manager, method, gap, js, urls, total_count=None, queue_timeout=90, delay=0):
    """ transmit all urls once, because ThinHash depends on
        modulo algroithm, must calculate modulo in the begining.
        Can not submit second job with same batch_id before first job finished.
    """
    import gevent
    from gevent import monkey; monkey.patch_all()

    total_count = len(urls) if len(urls) > 0 else total_count

    parameter = '{method}:{gap}:{js}:'.format(
            method=method,
            gap=gap,
            js=1 if js else 0)

    queue_dict = manager.init_distributed_queue(batch_id, parameter, total_count, timeout=queue_timeout)
    manager.put_urls_enqueue(batch_id, urls)

    return gevent.spawn_later(delay, queue_dict['queue'].background_cleaning)


def main():
    pass

if __name__ == '__main__':
    main()

