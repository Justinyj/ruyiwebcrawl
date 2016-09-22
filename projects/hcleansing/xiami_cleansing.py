# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import os
import paramiko
import time
import datetime
import pytz
import hashlib

from loader import slack



class XiamiDataMover(object):
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
            print abs_file_path



if __name__ == '__main__':
    a = XiamiDataMover()
    a.set_directory_list()
    a.read_and_insert(a.dir_list[0])