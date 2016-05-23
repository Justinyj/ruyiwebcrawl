#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from collections import OrderedDict
from agents import AGENTS_ALL
from proxy import Proxy

import random
import time

def choice_cookie(cookies):
    if not hasattr(choice_cookie, '_cookie'):
        setattr( choice_cookie,
                 '_cookie',
                 OrderedDict(sorted(cookies.items(), key=lambda x: x[0])) )

    if len(choice_cookie._cookie) == 0:
        setattr( choice_cookie,
                 '_cookie',
                 OrderedDict(sorted(cookies.items(), key=lambda x: x[0])) )

    _, cookie = choice_cookie._cookie.popitem()
    return cookie

def choice_agent():
    return random.choice(AGENTS_ALL)


def choice_proxy(config, url):
    while True:
        max_last_time = time.time() - config['CRAWL_GAP']
        proxies = Proxy.instance(config).get(url, max_last_time)
        if proxies is False:
            time.sleep(config['CRAWL_GAP'])
            print('lack of proxies, sleep') # TODO check
        else:
            protocol = proxies.split(':', 1)[0]
            return {protocol: proxies}
