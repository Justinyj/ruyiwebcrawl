#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from hprice_cleaning import HpriceCleansing
from datetime import datetime


class HpriceCleansing(object):
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.source_files_path = None
        self.counter = 0
        self.jsons = []

    def set_source_files_path(self):
        dir_path =  '/data/hproject/2016/' + self.dir_name
        
        if os.path.isdir(dir_path):  
            file_list = os.listdir(dir_path)
            self.source_files_path = [dir_path + '/' + file for file in file_list]
        else:
            raise IOError('no such directory: {}'.format(dir_path))


    def parse_single_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    item = json.loads(line.strip())
                    self.parse_single_item(item)
        sendto_es(self.jsons)
        self.counter = 0
        self.jsons = []


    def parse_single_item(self, item):
        pass

    def run(self):
        self.set_source_files_path()
        for file_path in self.source_files_path:
            self.parse_single_file(file_path)
