#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
import os
import sys
from rediscluster.redispool import RedisPool
from rediscluster.record import Record
from rediscluster.queues import Queue


def init():
    record = 'redis://172.31.19.253:6379/1'
    queue = 'redis://172.31.19.253:6379/2'
    cache = ['redis://172.31.19.253:6379/0',]
    RedisPool.instance(record, queue, cache)


def get_status(batch_id):
    if not hasattr(get_status, '_queue'):
        setattr(get_status, '_queue', Queue(batch_id))

    print('job {} remain {} url to crawl'.format(batch_id,
                get_status._queue.conn.scard(batch_id)))
    for key, value in Record.instance().conn.hgetall(batch_id).iteritems():
        print('\t{}: {}'.format(key, value))


def interval(val, func, arg):
    while 1:
        if val and sys.stdout.isatty():
            os.system('clear')
        func(arg)
        if val and sys.stdout.isatty():
            time.sleep(val)
        else:
            break


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(prog='python rediscluster/monitor.py',
                                     description='monitor rediscluster.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--batch_id', '-b', type=str, help='batch_id of the job')
    parser.add_argument('--interval', '-i', metavar='N', type=float, default=5, help='Updates stats every N seconds')
    return parser.parse_args(), parser


def main():
    args, parser = parse_args()
    init()

    try:
        if not args.batch_id:
            raise()
        interval(args.interval, get_status, args.batch_id)
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        parser.print_help()

if __name__ == '__main__':
    main()

