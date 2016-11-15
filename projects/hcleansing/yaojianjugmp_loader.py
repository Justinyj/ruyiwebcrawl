#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
import json
import os
import hashlib
import re
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from loader import Loader
from hzlib import libfile
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class YaojianjugmpLoader(Loader):
    def read_from_mapping(self):
        self.company_set = set()
        dir_path = os.path.abspath(os.path.dirname(__file__))
        mapping_file = 'gmpgsp_header_mapping.json'
        mapping_path = os.path.join(dir_path, mapping_file)
        with open(mapping_path) as f:
            self.header_mapping = json.load(f)

    def read_jsn(self, data_dir):
        self.jsons = []
        self.read_from_mapping()
        for fname in os.listdir(data_dir):
            for js in libfile.read_file_iter(os.path.join(data_dir, fname), jsn=True):
                self.parse(js)

    def parse(self, jsn):
        del jsn['source']
        del jsn['access_time']
        for key in jsn:
            if not  self.header_mapping.get(key, None):
                print key
        self.jsons.append(jsn)

    def output(self):
        keys = self.header_mapping.keys()
        header_set = list(set([self.header_mapping[key] for key in keys]))
        header_set.append(u'发布日期')
        print len(self.jsons)
        libfile.writeExcel(self.jsons, header_set,'test_DB.xls')

if __name__ == '__main__':
    obj = YaojianjugmpLoader()
    obj.read_jsn('/Users/johnson/yaojianjugmp-1104')
    obj.output()