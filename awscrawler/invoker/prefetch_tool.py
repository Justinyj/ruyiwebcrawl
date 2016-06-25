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
from operator import itemgetter

from awscrawler import post_job, delete_distributed_queue
from schedule import Schedule

VERSION ='v20160620'


def catch_terminate_instances_signal(schedule):
    gevent.signal(signal.SIGINT, schedule.stop_all_instances)
    gevent.signal(signal.SIGTERM, schedule.stop_all_instances)

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def slack(msg):
    data={
        "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))

def run(config):
    ts_start = time.time()

    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start load_urls --- dryrun mode')
    else:
        print(datetime.datetime.now().isoformat(), 'start load_urls --- work mode')

    mini_key = min(config["jobs"].keys())
    partial_url = config["jobs"][mini_key]["partial_url"] if "partial_url" in config["jobs"][mini_key] else None
    urls = load_urls(config["jobs"][mini_key]["filename_urls"], partial_url)

    slack( u"run {} batch_id: {}, urls length: {} debug: {}".format(
        config["note"],
        config["jobs"][mini_key]["batch_id"],
        len(urls),
        config.get("debug",False)) )


    tasks = []
    jobs = sorted(config["jobs"].iteritems(), key=itemgetter(0), reverse=False)
    for i, v in jobs:
        if i == mini_key:
            if config.get("debug"):
                print(datetime.datetime.now().isoformat(), 'start post_job ', v["batch_id"])

            t = post_job(
                v["batch_id"],
                v["crawl_http_method"],
                v["crawl_gap"],
                v["crawl_use_js_engine"],
                urls,
                len(urls) * v["length"],
                priority=v["priority"],
                queue_timeout=v["crawl_timeout"],
                failure_times=v['failure_times'])
        else:
            if config.get("debug"):
                print(datetime.datetime.now().isoformat(), 'start post_job with delay', v["batch_id"])

            t = post_job(
                v["batch_id"],
                v["crawl_http_method"],
                v["crawl_gap"],
                v["crawl_use_js_engine"],
                [],
                len(urls) * v["length"],
                priority=v["priority"],
                queue_timeout=v["crawl_timeout"],
                failure_times=v['failure_times'],
                start_delay=200)

        tasks.append(t)


    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'start instances')
    if not config.get("debug"):
        schedule = Schedule(config["aws_machine_number"],
                            tag=config["jobs"][mini_key]["batch_id"].split('-', 1)[0],
                            backoff_timeout=config["jobs"][mini_key]["crawl_timeout"])

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
        gevent.killall([t3], block=False)
        schedule.stop_all_instances()

    if config.get("debug"):
        print(datetime.datetime.now().isoformat(), 'all done.  --- dryrun mode')
    else:
        print(datetime.datetime.now().isoformat(), 'all done.  --- work mode')

    seconds = int(time.time() - ts_start)
    slack( "done {}, {} seconds".format(config["jobs"][mini_key]["batch_id"], seconds) )


def load_urls(fname, partial_url=None):
    import urllib
    ret = set()
    with open(fname) as fd:
        for line in fd:
            line = line.strip()
            #skip empty or comment line
            if not line or line.startswith('#'):
                continue

            url = line if partial_url is None else partial_url.format(urllib.quote(line))
            ret.add(url)
    return list(ret)

if __name__ == '__main__':
    """
        python invoker/prefetch_tool.py config_fudankg.json indexes
    """
    filename_config = getTheFile("../config_prefetch/" + sys.argv[1])
    config_index = sys.argv[2]
    with open(filename_config) as f:
        config_all = json.load(f)
        run(config_all[config_index])
    print ("all done!")
