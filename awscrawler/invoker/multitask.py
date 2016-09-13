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
from functools import partial
from rediscluster.queues import Queue

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

def get_failed_url(batch_id):
    queue = Queue(batch_id)
    count = 0

    for field, value in queue.get_failed_fields().iteritems():
        count += 1


    slack('spider has {} failed urls batch_id:{}'.format(count, batch_id))

def run(config):
    ts_start = time.time()
    today_str = datetime.datetime.utcnow().strftime('-%Y%m%d')

    if config.get("debug"):
        print(datetime.datetime.utcnow().isoformat(), 'start finding first job --- dryrun mode')
    else:
        print(datetime.datetime.utcnow().isoformat(), 'start finding first job --- work mode')

    mini_key = min(config["jobs"].keys())
    job = config["jobs"][mini_key]
    url_length = get_urls_length(job["filename_urls"])

    url_pattern = job["url_pattern"] if "url_pattern" in job else None
    urls_func = partial(load_urls, job["filename_urls"], url_pattern)

    if not config.get("debug"):
        slack( u"run {} batch_id: {}, urls length: {} debug: {}".format(
            config["note"],
            job["batch_id"] + today_str,
            url_length,
            config.get("debug", False)) )


    # 先开机器
    if config.get("debug"):
        print(datetime.datetime.utcnow().isoformat(), 'start instances')
    if not config.get("debug"):
        cookies = config["jobs"]["cookies"] if "cookies" in config["jobs"] else []
        schedule = Schedule(config["aws_machine_number"],
                            tag=config["jobs"][mini_key]["batch_id"],
                            backoff_timeout=config["jobs"][mini_key]["crawl_timeout"],
                            cookies=cookies)

        catch_terminate_instances_signal(schedule)

    print(datetime.datetime.utcnow().isoformat(), 'start post_job')

    tasks = [
        post_job(job["batch_id"] + today_str,
                 job["crawl_http_method"],
                 job["crawl_gap"],
                 job["crawl_use_js_engine"],
                 int(url_length * job["length"]),
                 urls_func=urls_func,
                 priority=job["priority"],
                 queue_timeout=job["crawl_timeout"],
                 failure_times=job.get('failure_times', 3))
    ]



    jobs = sorted(config["jobs"].iteritems(), key=itemgetter(0), reverse=False)
    for i, v in jobs:
        if i == mini_key:
            continue
        if i == "cookies":
            continue
        if "filename_urls" in v:
            v_url_length = get_urls_length(v["filename_urls"])
            v_url_pattern = v["url_pattern"] if "url_pattern" in v else None
            v_urls_func = partial(load_urls, v["filename_urls"], v_url_pattern)
        else:
            v_url_length = url_length
            v_urls_func = None

        print(datetime.datetime.utcnow().isoformat(), 'start post_job with delay')
        tasks.append( post_job(v["batch_id"] + today_str,
                               v["crawl_http_method"],
                               v["crawl_gap"],
                               v["crawl_use_js_engine"],
                               int(v_url_length * v["length"]),
                               urls_func=v_urls_func,
                               priority=v["priority"],
                               queue_timeout=v["crawl_timeout"],
                               failure_times=v.get('failure_times', 3),
                               start_delay=200)
                    )


    if config.get("debug"):
        print(datetime.datetime.utcnow().isoformat(), 'start spawn to run program in instances')
    if not config.get("debug"):
        t3 = gevent.spawn(schedule.run_forever)

    gevent.joinall(tasks)


    print(datetime.datetime.utcnow().isoformat(), 'job done. start delete_distributed_queue')
    for greenlet in tasks:
        ret = delete_distributed_queue(greenlet)
        print('{} return of delete {}'.format(ret, greenlet.value))


    if config.get("debug"):
        print(datetime.datetime.utcnow().isoformat(), 'killall')
    if not config.get("debug"):
        gevent.killall([t3], block=False)
        schedule.stop_all_instances()

    if config.get("debug"):
        print(datetime.datetime.utcnow().isoformat(), 'all done.  --- dryrun mode')
    else:
        print(datetime.datetime.utcnow().isoformat(), 'all done.  --- work mode')

    seconds = int(time.time() - ts_start)
    if not config.get("debug"):
        slack( "done {}, {} seconds".format(config["jobs"][mini_key]["batch_id"] + today_str, seconds) )
    for key in config["jobs"].keys():
        if key == 'cookies':
            continue
        batch_id = config["jobs"][key]["batch_id"]
        get_failed_url(batch_id)


def get_urls_length(fname):
    with open(fname) as fd:
        return len(fd.readlines())

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

            if len(ret) > 10000:
                yield list(ret)
                ret = set()
    if len(ret) > 0:
        yield list(ret)


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
