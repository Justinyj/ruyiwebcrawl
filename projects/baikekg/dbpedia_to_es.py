#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from hzlib.libfile import read_file_iter, write_file
from filter_lib import regdisambiguation
from to_es import send_definition_to_es

DIR = '/Users/bishop/百度云同步盘/'

def load_dbpedia():
    data = {}
    for line in read_file_iter(DIR + 'merge_step_5_simplified.json', jsn=True):
        for key, value in line.items():
            entity = value[u'resource_label']
            data[entity] = {}

            if u'short_abstract' in value:
                data[entity]['definition'] = value[u'short_abstract']

#            if u'resource_alias' in value:
#                data[entity]['aliases'] = value[u'resource_alias']

    send_definition_to_es(data, 'definition')
    return data

load_dbpedia()
