#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from hzlib.libfile import read_file_iter, write_file
from filter_lib import regchinese, regentityfilt


def begin_filter_with_chinese(fname):
    entities = set()
    for line in read_file_iter(fname):
        if regchinese.match(line.decode('utf-8')):
            entities.add(line)

    write_file('entities_chinese_2_10.txt', entities)


def begin_filter_with_lower(fname):
    entities = set()
    for line in read_file_iter(fname):
        entities.add( line.lower() )
    return entities

def begin_filter_with_search(fname):
    entities = set()

    for line in read_file_iter(fname):
        m = regentityfilt.match(line.decode('utf-8'))
        if m:
            entities.add( m.group(1) )

    return entities

if __name__ == '__main__':
    entities = set()
    entities.update( begin_filter_with_search('entities/first_order_entities.txt') )
    print('length of first order filtered entities', len(entities))
    entities.update( begin_filter_with_search('entities/second_order_entities.txt') )
    write_file('for_fudan_search_entity.txt', entities)
