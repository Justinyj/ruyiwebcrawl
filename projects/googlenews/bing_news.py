#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# 1000times/month for free in 3 month, every 1000 tims cost $3 per month

from __future__ import print_function, division

import urllib2
import requests

first_key = '9890d47685bd40bbb102d95473434bd9'
second_key = '79a82e2f8c3b46b28a8f8a69fffb1b2b'

mkt = 'zh-CN'
news_api = 'https://api.cognitive.microsoft.com/bing/v5.0/news/search'

headers = {
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Host': 'api.cognitive.microsoft.com',
    'Ocp-Apim-Subscription-Key': first_key
}

def search(word):
    '{}?q={}&mkt={}'.format(news_api, urllib2.quote(word), mkt)

