#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division

import os
import multiprocessing
import time
import json

from datetime import datetime
from multitask import run


def get_hcrawler_conf_dir():
    config_dir = os.path.dirname(os.path.join(os.path.abspath(__file__) ,'..'))
    return os.path.join(config_dir, 'config_prefetch/hcrawler')

def run_crawler(config_file):
    with open(config_file) as fd:
        config_all = json.load(fd)
        run(config_all['indexes'])

def split_crawl_jobs():
    now = datetime.now()
    conf_file = get_hcrawler_conf_dir()

    jobs = []
    if now.day == 1:
        p = multiprocessing.Process(target=run_crawler, args=(conf_file + "/daily.json",))
        jobs.append(p)
        p.start()
    if now.weekday() == 6: # Sunday
        p = multiprocessing.Process(target=run_crawler, args=(conf_file + "/daily.json",))
        jobs.append(p)
        p.start()

    p = multiprocessing.Process(target=run_crawler, args=(conf_file + "/daily.json",))
    jobs.append(p)
    p.start()
    for job in jobs:
        job.join()

def cleansing():
    pass

def insert_to_es():
    pass

def main():
    split_crawl_jobs()
    cleansing()
    insert_to_es()


if __name__ == '__main__':
    main()
