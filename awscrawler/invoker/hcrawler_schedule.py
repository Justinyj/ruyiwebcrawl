#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function, division

from multitask import run

import os
import datetime
import multiprocessing
import time
import json


def get_aws_file():
    return os.path.abspath(os.path.dirname(__file__)+'/..')

def fake_run(filename_config):
    with open(filename_config) as f:
        config_all = json.load(f)
        print config_all['indexes']
        #run(config_all['indexes'])

def set_jobs(job_list):
    file_path = get_aws_file() + '/config_prefetch/hcrawler'
    now = datetime.datetime.now()

    if now.day:# == 1:
        p = multiprocessing.Process(target=fake_run, args=(file_path + "/monthly.json",))
        job_list.append(p)
        p.start()

    if now.weekday():# % 7 == 0:
        p = multiprocessing.Process(target=fake_run, args=(file_path + "/weekly.json",))
        job_list.append(p)
        p.start()

    p = multiprocessing.Process(target=fake_run, args=(file_path + "/daily.json",))
    job_list.append(p)
    p.start()
    for job in job_list:
        job.join()



def main():
    job_list = [] 
    set_jobs(job_list)
    
if __name__ == '__main__':
    main()


