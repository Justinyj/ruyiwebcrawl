#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from settings import QUEUE_REDIS, RECORD_REDIS, CACHE_REDIS
from settings import REGION_NAME
from rediscluster.redispool import RedisPool
from rediscluster.queues import Queue

import json
import urllib
import re
import urlparse
import time

batch_id = 'searchzhidao2-20160728'
redispool = RedisPool.instance(RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS)

def get_failed_url():
    queue = Queue(batch_id)
    count = 0

    with open(batch_id + '.txt', 'w') as fd:
        for field, value in queue.get_failed_fields().iteritems():
            count += 1
            fd.write(value + '\n')
    print(count)

get_failed_url()
