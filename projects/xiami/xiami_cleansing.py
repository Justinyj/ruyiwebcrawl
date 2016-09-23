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


class XiamiDataMover(object):
    def __init__(self):
        self.count = 0
        self.jsons = []
        self.tags = set()

    def set_directory_list(self):
        origin_dir = ('/Users/johnson/xiami/music')
        dir_list = [origin_dir]
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
                        self.tags.add(tag)
                    with open('artisits.txt','a') as f:
                        f.write(item['artist'] + '\n')
                    with open('songname.txt','a') as f:
                        f.write(item['songName'] + '\n')
            except:
                with open('failed.txt','a') as f:
                    f.write(abs_file_path + '\n')
                print(abs_file_path)
                continue
            self.jsons.append(item)
            self.count += 1
            if self.count > 350:
                sendto_es(self.jsons)
                self.count = 0
                self.jsons = []
    def run(self):
        self.set_directory_list()
        for dir_path in self.dir_list:
            self.read_and_insert(dir_path)
        if self.jsons:
            sendto_es(self.jsons)
        with open('tags.txt', 'w') as f:
            for tag in self.tags:
                f.write(tag + '\n')


if __name__ == '__main__':
    mover = XiamiDataMover()
    mover.run()

