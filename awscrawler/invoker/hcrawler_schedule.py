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
    config_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
    return os.path.join(config_dir, 'config_prefetch/hcrawler')

def run_crawler(config_file):
    with open(config_file) as fd:
        config_all = json.load(fd)
        run(config_all['indexes'])

def split_crawl_jobs():
    now = datetime.now()
    conf_file = get_hcrawler_conf_dir()

    cpu_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpu_count * 10)

    if now.day == 1:
        pool.apply_async(run_crawler, (os.path.join(conf_file, 'monthly.json'), ))
    if now.weekday() == 6: # Sunday
        pool.apply_async(run_crawler, (os.path.join(conf_file, 'weekly.json'), ))
    pool.apply_async(run_crawler, (os.path.join(conf_file, 'daily.json'), ))

    pool.close()
    pool.join()

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
