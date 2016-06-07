#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# add answer api url to zhidao-answer-xxx queue

from __future__ import print_function, division

def worker(url, parameter, *args, **kwargs):
    method, gap, js, data = parameter.split(':')

