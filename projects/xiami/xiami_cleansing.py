# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import os
import time
import datetime
import hashlib
import sys
sys.path.append('..')

from cleansing_hcrawler.hprice_cleaning import  *
from collections import Counter

class XiamiDataMover(object):
    def __init__(self, origin_dir='/Users/johnson/xiami/music'):
        self.count = 0
        self.jsons = []
        self.origin_dir = origin_dir
        self.tag_counter = Counter()

    def set_directory_list(self):
        # 是一个层序遍历的函数，利用列表模拟队列
        # 输入：上级目录，得到：所有最下级目录
        dir_list = [self.origin_dir]
        while 1:
            directory = dir_list[0]
            sub_dir_list = os.listdir(directory)
            if not os.path.isdir(os.path.join(directory, sub_dir_list[0])):
                break
            else:
                for dirname in sub_dir_list:
                    dir_list.append(os.path.join(directory, dirname))    
                del dir_list[0]
        self.dir_list = dir_list

    def read_and_insert(self, dir_path):
        file_name_list = os.listdir(dir_path)
        for file_name in file_name_list:
            abs_file_path = os.path.join(dir_path, file_name)
            try:
                with open(abs_file_path, 'r') as f:
                    item = json.load(f)
                    for tag in item['tags']:
                        if tag[0:3] in ['AN:','BN:','MN:']:
                            continue
                        self.tag_counter[tag] += 1
                    with open('artisits.txt','a') as f:
                        f.write(item['artist'] + '\n')
                    with open('songname.txt','a') as f:
                        f.write(item['songName'] + '\n')
            except:
                with open('failed.txt','a') as f:
                    f.write(abs_file_path + '\n')
                continue
            self.jsons.append(item)
            self.count += 1
            if self.count > 350:     # 对于歌曲json，大于400会发送失败
                sendto_es(self.jsons)
                self.count = 0
                self.jsons = []

    def statistic_tags(self):     #  统计排名前100的tag
        print 'begin statistic'
        sorted_tags = []
        for tag, count in self.tag_counter.iteritems():
            sorted_tags.append([tag, count])

        self.tag_counter = []
        sorted_tags.sort(key=lambda ele:ele[1], reverse=1)
        with open('tags.txt', 'w') as f:
            for tag in sorted_tags:
                f.write('{}\t{}'.format(tag[0], tag[1]) + '\n')

    def run(self):
        self.set_directory_list()
        for dir_path in self.dir_list:
            self.read_and_insert(dir_path)
        if self.jsons:
            sendto_es(self.jsons)

        self.statistic_tags()



if __name__ == '__main__':
    mover = XiamiDataMover(origin_dir='/Users/johnson/xiami/music/crawl/latest')
    mover.run()
