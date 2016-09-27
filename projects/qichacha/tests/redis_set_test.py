#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>

# [TestInfo]:Insert 300000 entries | total time is 15.9282529354
# [TestInfo]:Read 300000 entries | total time is 15.9985508919
# [TestInfo]:Remove 300000 entries | total time is 16.1527490616
# [TestInfo]:Insert 500000 entries | total time is 27.0461318493
# [TestInfo]:Read 500000 entries | total time is 26.4595499039
# [TestInfo]:Remove 500000 entries | total time is 26.7188289165
# [TestInfo]:Insert 1000000 entries | total time is 53.8090929985
# [TestInfo]:Read 1000000 entries | total time is 52.761950016
# [TestInfo]:Remove 1000000 entries | total time is 53.4860301018
# [TestInfo]:Insert 2000000 entries | total time is 108.064925909
# [TestInfo]:Read 2000000 entries | total time is 105.540910006
# [TestInfo]:Remove 2000000 entries | total time is 106.879275084

from __future__ import print_function, division


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import redis
import json
import time


TOTAL = [300000, 500000, 1000000, 2000000]
PASS = ""

class RedisSpeedTest(object):
    def __init__(self, host, port, db, password=None):
        self.client = redis.StrictRedis(host=host, port=port, db=db, password=password)
    
    def file_read_time(self, fname, number):
        i = 0
        start = time.time()
        file = open(fname, 'r')
        for line in file:
            i += 1
            if i == number:
                break
        file.close()
        return time.time() - start
                
    
    
    def test_insert(self, fname, number):
        start = time.time()
        i = 0
        file = open(fname, 'r')
        for line in file:
            self.client.sadd('qichacha', line.strip())
            i += 1
            if i == number:
                break
        total_time = (time.time() - start)
        print("[TestInfo]:Insert {} entries | total time is {}".format(number, total_time))

    def test_read(self, fname, number):    
        start = time.time()
        i = 0
        file = open(fname, 'r')
        for line in file:
            self.client.sismember('qichacha', line.strip())
            i += 1
            if i == number:
                break
        total_time = (time.time() - start) 
        print("[TestInfo]:Read {} entries | total time is {}".format(number, total_time))
        file.close()

    def test_remove(self, fname, number):
        i = 0
        file = open(fname, 'r')
        start = time.time()
        for line in file:
            self.client.srem('qichacha', line.strip())
            i += 1
            if i == number:
                break
        total_time = (time.time() - start)
        print("[TestInfo]:Remove {} entries | total time is {}".format(number, total_time))
        file.close()
        self.client.delete('qichacha')

if __name__ == '__main__':
    fname = 'mlj_all_data.txt'
    tester = RedisSpeedTest(host='localhost', port=6379, db=3, password=PASS)
    for t in TOTAL:
        # print(tester.file_read_time(fname, t))
        tester.test_insert(fname, t)
        tester.test_read(fname, t)
        tester.test_remove(fname, t)


# for member in client.smembers("qichacha"):
#     print member

# print 'the size of our set is: %s'% client.scard("qichacha")
# print client.sismember("qichacha", "泰州市扬子江胶囊厂")