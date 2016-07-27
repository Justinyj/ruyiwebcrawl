#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
import string
import random
import requests
import json
import os
import time
import subprocess
from datetime import datetime

ENV = 'test'
#  os.system("echo -n %s $(ls -al /proc/`ps aux | grep jsvc | grep -v grep | awk {'print $2'} | sort -r | head -n 1`/fd | wc -l) >> monitor.log" % datetime.now().isoformat())

def slack(msg):
    data = { "text": msg }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))


def mongo_connection():
    cmd = 'netstat -antp | grep 27017 | wc -l'
    ret = run(cmd).split('\n')[-1]
    if ret == '':
        ret = '-1'
    result = int(ret)
    if result > 4096:
        slack('{} server mongo conn: {}'.format(ENV, result))

    return ret

def connection():
    cmd = 'netstat -antp | wc -l'
    ret = run(cmd).split('\n')[-1]
    if ret == '':
	   ret = '-1'
    result = int(ret)
    if result > 4096:
        slack('{} server conn: {}'.format(ENV, result))

    return ret

def jsvc_thread():
    cmd = "pstree | grep jsvc | awk -F'-' {'print $NF'}"
    ret = run(cmd)
    if ret == '':
	   ret = '-1'
    result = int( ret[:ret.find('*')] )
    if result > 2048:
        slack('{} server jsvc thread: {}'.format(ENV, result))

    return ret[:ret.find('*')]

def jsvc_fd():
    cmd = "ls -al /proc/`ps aux | grep jsvc | grep -v grep | awk {'print $2'} | sort -r | head -n 1`/fd | wc -l"
    ret = run(cmd)
    if ret == '':
	   ret = '-1'	
    result = int(ret)
    if result > 2048:
        slack('{} server jsvc fd: {}'.format(ENV, result))

    return ret

def run(cmd):
    from subprocess import Popen, PIPE, STDOUT
    p = Popen(cmd, close_fds=True, shell=True, stdout=PIPE, stderr=None)
    while p.poll() is None:
        out = p.stdout.read()
    return out.strip()


def random_url(url, length=4):
    chars = string.letters + string.digits
    s = ''.join(random.Random().sample(chars, length))
    return url.format(s)

def get_running_stat(url_temlate):
    url = random_url(url_temlate)
    for _ in range(3):
        response = requests.get(url)
        if response.status_code == 200:
            break
    else:
        slack
        return False
    res = response.json()
    process_milliseconds = res['result']['meta_process_milliseconds']


    return process_milliseconds

def main():
    #min_ms的判断：为了增强健壮性，只有当一个时间区间内的延迟最小值超过500ms才会报错，而不是一次判断超出500就报错。
    counter = 0
    min_ms = 999
    while 1:
        line = [datetime.now().isoformat()]
        line.append( mongo_connection() )
        line.append( connection() )
        line.append( jsvc_thread() )
        line.append( jsvc_fd() )
        process_ms = get_running_stat('http://api.ruyi.ai/v1/message?app_key=28b12c3d-fab6-4540-af27-460277aa1a58&user_id=123&q={}')
        if process_ms：
            line.append( str(process_ms) )
        fd = open('monitor.log', 'a')
        fd.write( '\t'.join(line) + '\n' )
        fd.close()

        min_ms = min(min_ms, process_ms)
        counter += 1
        if counter == 6:
            if min_ms >  500:
                slack('{} server high process_millisecons in 3 mins : {}'.format(ENV, min_ms))
                #print 'send a message'
            counter = 0
            min_ms = 999

        time.sleep(30)

if __name__ == '__main__':
    main()
