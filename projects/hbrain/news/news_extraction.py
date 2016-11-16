#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import urllib2
import requests

class NewsExtraction(object):

    def __init__(self):
        self.api_url = 'http://api.ruyi.ai/v1/message?app_key=0df50fac-4df0-466c-9798-99136f42bb8c&user_id=123&q={}'

    def call_api(self, sentence):
        url = self.api_url.format(urllib2.quote(sentence))
        ret = requests.get(url)
        print( json.dumps( ret.json(), ensure_ascii=False, indent=True) )

obj = NewsExtraction()
obj.call_api('快讯：桔梗火热，种子价连涨有望突破150元！')

