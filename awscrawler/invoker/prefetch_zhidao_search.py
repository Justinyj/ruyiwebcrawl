#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import gevent
import time
import datetime
import time
import os
import sys
import requests
import json
from awscrawler import post_job, delete_distributed_queue
from schedule import Schedule

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

###########
# config parameters
THE_CONFIG = {
    "batch_id": 'zhidao-search-20160619',
    "crawl_http_method" : "get",
    "crawl_gap" : 3,
    "crawl_use_js_engine" : False,
    "crawl_timeout" : 10,
#    "crawl_refresh" : False,
#    "crawl_result_content_encoding" : 'gb18030',
#    "crawl_http_headers": {'Host': 'zhidao.baidu.com'},
    "aws_machine_number" : 40,

    # ln -s /Users/lidingpku/haizhi/project/ruyiwebcrawl/awscrawler/local/
    "filename_urls" : '/data/awscrawler/local/zhidao_search/urls.20160617.raw.txt'
#    "debug" : True,
}

def slack(msg):
    data={
        "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))

def run(config):
    slack( "run {} debug: {}".format(config["batch_id"], config.get("debug",False)) )
    ts_start = time.time()

    #load urls
    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start load_urls --- dryrun mode')
    else:
        print(datetime.datetime.now().isoformat(), 'start load_urls --- work mode')
    urls = load_urls(config["filename_urls"])


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start post_job')
    tasks = []
    t1 = post_job(
        config['batch_id'],
        config['crawl_http_method'] ,
        config['crawl_gap'],
        config["crawl_use_js_engine"],
        urls,
        priority=2,
        queue_timeout=config['crawl_timeout'])
    tasks.append(t1)


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start instances')
    if not config.get("debug"):
        schedule = Schedule(    config['aws_machine_number'],
                            tag=config['batch_id'],
                            backoff_timeout=config['crawl_timeout'])



    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start job, spawn')
    if not config.get("debug"):
        t3 = gevent.spawn(schedule.run_forever)

    gevent.joinall(tasks)


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'job done. start delete_distributed_queue')
    for greenlet in tasks:
        ret = delete_distributed_queue(greenlet)
        print('{} return of delete {}'.format(ret, greenlet.value))


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'killall')
    if not config.get("debug"):
        gevent.killall([t3], block=True)
        schedule.stop_all_instances()

    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'all done.  --- dryrun mode')
    else:
        print(datetime.datetime.now().isoformat(), 'all done.  --- work mode')

    seconds = int(time.time() - ts_start)
    slack( "done {}, {} seconds".format(config["batch_id"], seconds) )


def load_urls(fname):
    ret = set()
    with open(fname) as fd:
        for line in fd:
            line = line.strip()
            #skip empty or comment line
            if not line or line.startswith('#'):
                continue

            ret.add(line)
    return list(ret)

if __name__ == '__main__':
    run(THE_CONFIG)
