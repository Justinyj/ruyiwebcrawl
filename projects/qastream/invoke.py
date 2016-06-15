#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from zhidao.zhidao_scheduler import Scheduler
CACHESERVER = 'http://192.168.1.179:8000'

s = Scheduler.instance(CACHESERVER)
ret = s.run('晚上吃什么有益健康', gap=3)
print(ret)
