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
    def __init__(self, origin_dir='/data/xiami/music/xiami-1009failed4'):
        self.count = 0
        self.jsons = []
        self.origin_dir = origin_dir
        self.tag_counter = Counter()

    def calculate_score(self, artist_fans, song_share, comment_cnt):
        return artist_fans * 0.001 + song_share * 0.599 + comment_cnt * 0.4

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
                dir_list.pop(0)
        self.dir_list = dir_list

    def clean_dot(self, word):
        word = re.sub(u'[·-‧()•]・', u'',word)
        dot_list = [u'·', u'-', u'‧', u'(', u')', u'•', u'・']
        for dot in dot_list:
            word = word.replace(dot, u'')
        return word

    def clean_single_song(self, song):
        song_item = song.copy()
        song_item['artist_fans'] = song_item['fans']
        del song_item['fans']                                   # 将fans字段替换成artist_fans

        try:
            alias_string = self.clean_dot(song_item['artist_alias']).strip()
        except:
            print 'aho'
            return
        song_item['artist_alias'] = [song[u'artist']]           # 按照知识图谱的习惯，别名里第一个为歌手本名

        if u'&' in song[u'artist']:
            song_item['artist_alias'].extend(song[u'artist'].split(u'&'))
        elif u' x ' in song[u'artist']:
            song_item['artist_alias'].extend(song[u'artist'].split(u' x '))

        if alias_string:
            song_item['artist_alias'].extend(alias_string.split(u'/'))

        for index in range(len(song_item['artist_alias'])):
            alias = self.clean_dot(song_item['artist_alias'][index]).strip()
            song_item[u'artist_alias'][index]  = alias
            song_item[u'tags'].append(u'AN:{}'.format(alias))

        song_item[u'name'] = song_item[u'name'].replace(u'(Live)', '').replace(u'(现场版)', '').strip()
        song_item[u'name'] = self.clean_dot(song_item['name'])
        song_item[u'songName'] = song_item[u'name']
        song_item[u'tags'].append(u'MN:{}'.format(song_item[u'name']))
        song_item[u'tags'].append(u'BN:{}'.format(song_item[u'album'].strip()))
        song_item[u'hot_score'] = self.calculate_score(song_item[u'artist_fans'], song_item[u'song_share'], song_item[u'comment_cnt'])

        with open('alias.txt', 'a') as f:
            f.write('\t'.join(song_item['artist_alias'])+'\n')
        
        self.jsons.append(song_item)
        self.count += 1
        if self.count == 300:              # 说明，由于部分歌曲歌词很长，每次发送300个json可能会使data大小超出es服务器的限制
            try:                           # 但是每次发送100个又会使es插入速度太慢，所以采取这种优先发送300个，失败后再分开发送
                sendto_es(self.jsons)
            except:
                sendto_es(self.jsons[0:50])
                sendto_es(self.jsons[50:100])
                sendto_es(self.jsons[100:150])
                sendto_es(self.jsons[150:200])
                sendto_es(self.jsons[200:250])
                sendto_es(self.jsons[250:])
            self.count = 0
            self.jsons = []

    def statistic_one_song(self, item):
        for tag in item['tags']:
            if tag[0:3] in ['AN:','BN:','MN:']:  # AN歌手名，BN专辑名，MN歌曲名，是在爬取过程中二次加入的，（如 AN:周杰伦 MN：晴天 ）。
              continue
            else:
                self.tag_counter[tag] += 1

        with open('artisits.txt','a') as f:
            f.write(item['artistid'] + '\n')

        with open('songname.txt','a') as f:
            f.write(item['songName'] + '\n')


    def read_and_insert(self, dir_path):
        file_name_list = os.listdir(dir_path)
        for file_name in file_name_list:
            abs_file_path = os.path.join(dir_path, file_name)
            with open(abs_file_path, 'r') as f:
                song_list = json.load(f)
                for song in song_list:
                    song[u'tags'] = song[u'tags'][:-3]  # 后续数据需求变化，删除tags里的AN BN MN，在清洗过程中重新加入
                    if u'&' in song[u'artist']:
                        song[u'tags'] = song[u'tags'][:-1]
                    self.clean_single_song(song)
                    #self.statistic_one_song(song)


    def statistic_tags(self):           #  歌曲tag排序
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
            print 'end'
            sendto_es(self.jsons)

        # self.statistic_tags()



if __name__ == '__main__':
    mover = XiamiDataMover()
    mover.run()
