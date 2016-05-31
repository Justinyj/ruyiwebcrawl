#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from agents import AGENTS_ALL
from proxy import Proxy

import random
import time

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
}

def choice_agent():
    return random.choice(AGENTS_ALL)


def choice_proxy(url, gap=0):
    while True:
        max_last_time = time.time() - gap
        proxies = Proxy.instance().get(url, max_last_time)
        if proxies is False:
            time.sleep(max(gap, 1))
            print('lack of proxies, sleep') # TODO check
        else:
            protocol = proxies.split(':', 1)[0]
            return {protocol: proxies}

