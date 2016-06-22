#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

#import signal
from gevent import signal

class Schedule(object):
    def __init__(self, num):
        self.num = num

    @classmethod
    def instance(cls, *args):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', cls(*args))
        return cls._instance

    def stop(self, signum=15, frame=None):
        print(self.num * 10)

def signal_handler(signum, frame):
    Schedule.instance().stop()

def init(schedule):
    signal.signal(signal.SIGINT, schedule.stop)
    signal.signal(signal.SIGTERM, schedule.stop)
#    signal.signal(signal.SIGKILL, signal_handler) # this must run as root

schedule = Schedule.instance(5)
init(schedule)

import time
time.sleep(10)
