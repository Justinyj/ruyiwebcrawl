#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, division

import os
import datetime
from settings import REGION_NAME, ENV




def get_config_file():
    file_path = os.path.abspath(os.path.dirname(__file__)+'/config_prefetch/hcrawler') 
    now = datetime.datetime.now()
    day_of_month = now.day
    if day_of_month  == 1:
        return file_path + "/monthly.json"

    day_of_week = now.weekday()
    if day_of_week % 7 == 0:
        return file_path + "/weekly.json"

    return file_path + "/daily.json"
print get_config_file()

def run(config_file):
    os.system('python invoker/prefetch_tool.py {} indexes'.format(config_file))
