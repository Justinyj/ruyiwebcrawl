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
        self.connect()

    def connect(self):
        self.conn = RedisPool.instance().record

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
        self.conn.hsetnx(batch_id, 'parameter', parameter)
        self.conn.hsetnx(batch_id, 'start', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.conn.hsetnx(batch_id, 'total', total)

        self.conn.hsetnx(batch_id, 'failed', 0)
        self.conn.hsetnx(batch_id, 'success', 0)

    def is_finished(self, batch_id):
        ret = self.conn.hget(batch_id, 'end')
        return False if ret is None else True

    def if_not_finish_set(self, batch_id):
        """ Returns 1 if HSETNX created a field, otherwise 0.
            atomic operation.
        """
        return self.conn.hsetnx(batch_id,
                                'end',
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def increase_success(self, batch_id, count=1):
        self.conn.hincrby(batch_id, 'success', count)

    def increase_failed(self, batch_id, count=1):
        self.conn.hincrby(batch_id, 'failed', count)

    def get_total_number(self, batch_id):
        return self.conn.hget(batch_id, 'total')

    def get_parameter(self, batch_id):
        return self.conn.hget(batch_id, 'parameter')

    def get_unfinished_batch(self):
        keys = []
        for key in self.conn.keys('*'):
            try:
                if self.is_finished(key) is False:
                    keys.append(key)
            except ResponseError:
                continue
        return keys
