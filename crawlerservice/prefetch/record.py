#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from datetime import datetime

import re

from settings import RECORD_REDIS

class Record(object):
    def __init__(self):
        host, port, db = re.compile('(.+):(\d+)/(\d+)').search(RECORD_REDIS).groups()
        self.conn = redis.Redis(host=host, port=int(port), db=int(db))

        self.jobs_key = 'jobskey'
        self.START = 0
        self.STOP = 1

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls()
        return cls._instance


    def start(self, batch_id, parameter, total):
        """ before task finish, it is a reentrant function

        :param batch_id: str
        :param parameter: str
        """
        self.conn.hsetnx(self.jobs_key, batch_id, self.START)

        self.conn.hsetnx(batch_id, 'parameter', parameter)
        self.conn.hsetnx(batch_id, 'start', datetime.now())
        self.conn.hsetnx(batch_id, 'end', 0)
        self.conn.hsetnx(batch_id, 'failed', 0)
        self.conn.hsetnx(batch_id, 'success', 0)
        self.conn.hincrby(batch_id, 'total', total)


    def stop(self, batch_id):
        self.conn.hset(self.jobskey, batch_id, self.STOP)
