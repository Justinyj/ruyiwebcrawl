#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import redis

key = 'test'
conn = redis.StrictRedis()
#for i in xrange(10**7):
#    conn.hset(key, i, 0)


def get():
    """ output will grow gradually to 1132
    """
    global conn
    count = 0
    next_seq = 0
    items = {}
    while not items:
        next_seq, items = conn.hscan(key, cursor=next_seq)
        count += 1
        if next_seq == 0:
            return True
    print(count)

    for i in items:
        conn.hdel(key, i)

while 1:
    if get():
        break
