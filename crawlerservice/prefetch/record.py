#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from datetime import datetime
from redis import ResponseError

from redispool import RedisPool

class Record(object):
    """ preserve all task(`batch_id`) status.
    """
    def __init__(self):
# 'jobskey' is a hashkey used in global service
#        self.jobs_key = 'jobskey'
#        self.START = 0
#        self.STOP = 1

        self.connect()

    def connect(self):
        self.conn = RedisPool.instance().record.get_connection(None)

    def disconnect(self):
        RedisPool.instance().record.release(self.conn)

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            if not hasattr(cls, '_instance'):
                cls._instance = cls()
        return cls._instance


    def begin(self, batch_id, parameter, total):
        """ before task finish, it is a reentrant function

        :param batch_id: str
        :param parameter: str
        """
#        self.conn.hsetnx(self.jobs_key, batch_id, self.START)

        self.conn.hsetnx(batch_id, 'parameter', parameter)
        self.conn.hsetnx(batch_id, 'start', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.conn.hincrby(batch_id, 'total', total)

        self.conn.hsetnx(batch_id, 'end', 0)
        self.conn.hsetnx(batch_id, 'failed', 0)
        self.conn.hsetnx(batch_id, 'success', 0)


    def end(self, batch_id):
#        self.conn.hset(self.jobskey, batch_id, self.STOP)
        self.conn.hset(batch_id, 'end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    def is_finished(self, batch_id):
        ret = self.conn.hget(batch_id, 'end')
        return False if ret == '0' else True

    def increase_success(self, batch_id, count=1):
        self.conn.hincrby(batch_id, 'success', count)

    def increase_failed(self, batch_id, count=1):
        self.conn.hincrby(batch_id, 'failed', count)

    def get_unfinished_batch(self):
        keys = []
        for key in self.conn.keys('*'):
            try:
                if self.is_finished(key) is False:
                    keys.append(key)
            except ResponseError:
                continue
        return keys

