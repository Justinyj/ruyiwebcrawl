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
import signal

from awscrawler import post_job, delete_distributed_queue
from schedule import Schedule

VERSION ='v20160620'


def catch_terminate_instances_signal(schedule):
    signal.signal(signal.SIGINT, schedule.stop_all_instances)
    signal.signal(signal.SIGTERM, schedule.stop_all_instances)

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def slack(msg):
    data={
        "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))

def run(config):
    ts_start = time.time()
    urls = load_urls(config["filename_urls"])

    slack( u"run {} batch_id: {}, urls: {} debug: {}".format(
        config["note"],
        config["batch_id"],
        len(urls),
        config.get("debug",False)) )


    #load urls
    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start load_urls --- dryrun mode')
    else:
        print(datetime.datetime.now().isoformat(), 'start load_urls --- work mode')


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start post_job')

    tasks = []
    for i in range(config['job_num']):
        if i == 0:
            t = post_job(
                config["batch_id"][i],
                config['crawl_http_method'] ,
                config['crawl_gap'][i],
                config["crawl_use_js_engine"],
                urls,
                len(urls) * config['length'][i],
                priority=config["priority"][i],
                queue_timeout=config['crawl_timeout'])
        else:
            t = post_job(
                config["batch_id"][i],
                config['crawl_http_method'] ,
                config['crawl_gap'][i],
                config["crawl_use_js_engine"],
                [],
                len(urls) * config['length'][i],
                priority=config["priority"][i],
                queue_timeout=config['crawl_timeout'],
                start_delay=180)

        tasks.append(t)


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start instances')
    if not config.get("debug"):
        schedule = Schedule(    config['aws_machine_number'],
                            tag=config['batch_id'][0].split('-', 1)[0],
                            backoff_timeout=config['crawl_timeout'])

        catch_terminate_instances_signal(schedule)


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
    """
        python invoker/prefetch_tool.py config_dongfangcaifu.json prefetch_index
    """
    filename_config = getTheFile("../config_prefetch/"+sys.argv[1])
    config_index = sys.argv[2]
    with open(filename_config) as f:
        config_all = json.load(f)
        run(config_all[config_index])
    print ("all done!")
