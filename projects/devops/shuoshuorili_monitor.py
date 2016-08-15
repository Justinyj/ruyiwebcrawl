#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import json
import os
import time
import requests

from datetime import datetime, timedelta



def slack(msg):
    data = { "text": msg }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))


def weixin_log(date_str):
    log_file = '/data/logs/smartv-weixin.log.{}'.format(date_str)
    return os.path.exists(log_file)


def schedule():
    while True:
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        ret = weixin_log(yesterday_str)
        if not ret:
            slack('shuoshuorili do not have weixin log in {}'.format(yesterday_str))
        time.sleep(86400)

if __name__ == '__main__':
    schedule()
