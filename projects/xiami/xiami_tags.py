# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import numpy as np
import numpy
import os
import time
import datetime
import hashlib
import sys
import re
import csv
import json
sys.path.append('..')

from collections import Counter

# a = [1,2]
# b = [10,20]


def cosine(vector1, vector2):
    l1 = np.sqrt(vector1.dot(vector1))
    l2 = np.sqrt(vector2.dot(vector2))
    return vector1.dot(vector2)/(l1*l2)

# print numpy.sqrt(numpy.sum(numpy.square(a - b)))  
class XiamiDataMover(object):
    def __init__(self, origin_dir='/data/crawler_file_cache/xiami-1015/raw/latest/0/11'):
        origin_dir = '/Users/johnson/google/11'
        self.origin_dir = origin_dir
        self.tag_counter = Counter()
        self.tag_pairs      = []
        self.tag_pairs_count = Counter()
        self.song_count = 0
        self.matrix     = {}
        with open('tags_top_450.txt') as f:
            for line in f:
                self.tag_pairs.append(line.strip().split('\t'))
                tag1 = line.strip().split('\t')[0].decode('utf-8')
                tag2 = line.strip().split('\t')[1].decode('utf-8')
                if tag1 not in self.matrix:
                    self.matrix[tag1] = {}
                self.matrix[tag1][tag2] = 0
                self.matrix[tag1][tag1] = 0
                if tag2 not in self.matrix:
                    self.matrix[tag2] = {}
                self.matrix[tag2][tag1] = 0
                self.matrix[tag2][tag2] = 0

    def set_directory_list(self):
        # 是一个层序遍历的函数，利用列表模拟队列
        # 输入：上级目录，得到：所有最下级目录
        # 注意break条件的判断，这是出于默认所有file同级下方可使用（即树的所有树叶深度相同），以适应aws的储存逻辑，如果不全同级则要更改判断条件
        dir_list = [self.origin_dir]
        while 1:
            directory = dir_list[0]
            sub_dir_list = os.listdir(directory)
            if not os.path.isdir(os.path.join(directory, sub_dir_list[0])):
                break
            else:
                for dirname in sub_dir_list:
                    dir_list.append(os.path.join(directory, dirname))    
                dir_list.pop(0)
        self.dir_list = dir_list


    def clean_tags(self, song_item):
        tags = song_item['tags']
        cleaned_tags = []
        for tag in tags:
            cleaned_tags.extend(tag.split(u' '))        # 处理空格
        cleaned_tags = list(set(cleaned_tags))            # 去重
        tags = cleaned_tags

        for i in tags:
            self.tag_counter[i] += 1

        for tag in tags:
            if tag in self.matrix:
                for tag2 in tags:
                    if tag2 in self.matrix[tag]:
                        self.matrix[tag][tag2] += 1
        return
        for tag_pair in self.tag_pairs:
            tag1, tag2 = tag_pair[0], tag_pair[1]
            if tag1.decode('utf-8') in tags and tag2.decode('utf-8') in tags:
                self.matrix[tag1][tag2] = 1
                self.matrix[tag2][tag1] = 1
                self.tag_pairs_count['{}\t{}'.format(tag1, tag2)] += 1
                print tag1, tag2
                # print self.tag_counter['回忆']


    def read_and_insert(self, dir_path):
        file_name_list = os.listdir(dir_path)
        for file_name in file_name_list:
            abs_file_path = os.path.join(dir_path, file_name)
            with open(abs_file_path, 'r') as f:
                song_list = json.load(f)
                for song in song_list:
                    self.song_count += 1
                    self.clean_tags(song)


    def output(self):
        keys = self.matrix.keys()
        with open('output.xls', 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # row = ['\\']
            # row = [key.encode('utf-8') for key in keys]
            # spamwriter.writerow(row)

            row = ['table head']
            row.append('好听')
            spamwriter.writerow(row)
            big = 0
            for i in keys:
                row = [i.encode('utf-8')]
                j = u'好听'
                row.append(self.matrix[i][j])
                if j ==u'华语':
                    print self.matrix[i][j]
                spamwriter.writerow(row)
    


    def run(self):
        self.set_directory_list()

        for dir_path in self.dir_list:
            self.read_and_insert(dir_path)      # 再遍历第二遍，进行清洗和插入操作
        res = self.tag_pairs_count.most_common()
        print self.song_count
        # print json.dumps(self.matrix[u'好听'][u'好听'], ensure_ascii=False)

        self.output()
        return
        with open('result.txt','w') as f:
            for ele in res:
                tag1 = ele[0].split('\t')[0]
                tag2 = ele[0].split('\t')[1]
                num1 =  float(self.tag_counter[tag1.decode('utf-8')])
                num2 =  float(self.tag_counter[tag2.decode('utf-8')])
                pxy  =  float(ele[0])
                f.write(ele[0] + ':' + str(ele[1]) + '\t' + str(num1) + '\t' + str(num2) +'\n')


if __name__ == '__main__':
    mover = XiamiDataMover()
    mover.run()



