#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>

# 测试机器类型: Linux ip-172-31-28-118 3.16.0-4-amd64 #1 SMP Debian 3.16.7-ckt25-1 (2016-03-06) x86_64 GNU/Linux, AWS medium instance
# Redis version: Redis server v=2.8.17 sha=00000000:0 malloc=jemalloc-3.6.0 bits=64 build=4c1d5710660b9479



# Redis server CPU usage: 38%  MEM usage: 5% 基本保持稳定, 数据来自 top 命令 , 与psutil观测结果一致
# [TestInfo]:Insert 300000 entries | total time is 16.7127320766 avg time per 10000 entries: 0.557091069221
# [TestInfo]:Read 300000 entries | total time is 16.444067955 avg time per 10000 entries: 0.548135598501
# [TestInfo]:Remove 300000 entries | total time is 16.6662759781 avg time per 10000 entries: 0.555542532603
# [TestInfo]:Insert 500000 entries | total time is 27.9345479012 avg time per 10000 entries: 0.558690958023
# [TestInfo]:Read 500000 entries | total time is 27.4593861103 avg time per 10000 entries: 0.549187722206
# [TestInfo]:Remove 500000 entries | total time is 27.7590019703 avg time per 10000 entries: 0.555180039406
# [TestInfo]:Insert 1000000 entries | total time is 55.8296020031 avg time per 10000 entries: 0.558296020031
# [TestInfo]:Read 1000000 entries | total time is 54.9254832268 avg time per 10000 entries: 0.549254832268
# [TestInfo]:Remove 1000000 entries | total time is 55.5710198879 avg time per 10000 entries: 0.555710198879
# [TestInfo]:Insert 2000000 entries | total time is 111.925565958 avg time per 10000 entries: 0.55962782979
# [TestInfo]:Read 2000000 entries | total time is 109.971976995 avg time per 10000 entries: 0.549859884977
# [TestInfo]:Remove 2000000 entries | total time is 111.371142864 avg time per 10000 entries: 0.556855714321
# 由此可见redis set 插入\读取\删除速度在当前量级下基本保持不变, 均为0.55~0.56秒每万次操作, 即数据量并不影响redis操作速度.
from __future__ import print_function, division


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import redis
import json
import time


TOTAL = [300000, 500000, 1000000, 2000000]


class RedisSpeedTest(object):
    def __init__(self, host, port, db, password=None):
        self.client = redis.StrictRedis(host=host, port=port, db=db)
    
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
        print("[TestInfo]:Insert {} entries | total time is {}".format(number, total_time), "avg time per 10000 entries:", total_time / number * 10**4)

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
        print("[TestInfo]:Read {} entries | total time is {}".format(number, total_time), "avg time per 10000 entries:", total_time / number * 10**4)
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
        print("[TestInfo]:Remove {} entries | total time is {}".format(number, total_time), "avg time per 10000 entries:", total_time / number * 10**4)
        file.close()
        self.client.delete('qichacha')

if __name__ == '__main__':
    fname = 'mlj_all_data.txt'
    tester = RedisSpeedTest(host='localhost', port=6379, db=3)
    for t in TOTAL:
        # print(tester.file_read_time(fname, t))
        tester.test_insert(fname, t)
        tester.test_read(fname, t)
        tester.test_remove(fname, t)


# for member in client.smembers("qichacha"):
#     print member

# print 'the size of our set is: %s'% client.scard("qichacha")
# print client.sismember("qichacha", "泰州市扬子江胶囊厂")
