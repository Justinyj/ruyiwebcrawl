#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from awscrawler import post_job


def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']

urls = load_urls()
post_job('zhidao-question-20160607', 'get', 3, urls)
post_job('zhidao-answer-20160607', 'get', 3, [])
schedule = Schedule(10, tag=batch_id.split('-', 1)[0])
schedule.run()
