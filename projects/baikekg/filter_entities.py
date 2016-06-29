#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
from load_entities import read_file_iter, write_file

regchinese = re.compile(u'^[\u4e00-\u9fff]{2,10}$')

def filter_entities(ifilename):
    entities = set()
    for line in read_file_iter(ifilename):
        if regchinese.match(line.decode('utf-8')):
            entities.add(line)

    write_file('entities_chinese_2_10.txt', entities)

filter_entities('ent.txt')
