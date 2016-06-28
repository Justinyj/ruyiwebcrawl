#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from algorithm import combination
from load_file import read_file, write_file

DIR = '/Users/bishop/百度云同步盘/'

def get_attributes(dirname='fudankg-json'):
    attributes = Counter()

    for f in os.listdir(dirname):
        jsn = read_file(os.path.join(dirname, f), ret='json')
        for entity, avps in jsn.items():
            for a, v in avps:
                attributes[a] += 1

    items = sorted(attributes.items(), key=itemgetter(1), reverse=True)

    wfname = os.path.join(DIR, 'attributes.txt')
    write_file(wfname, items, jsn=True)


def attr_clustering(fname):
    with open(fname) as fd:
        content = json.load(fd)
    attributes = [i[0] for i in content]
    groups = combination(attributes)

    wfname = os.path.join(DIR, 'attributes_in_groups.txt')
    write_file(wfname, groups, jsn=True)


if __name__ == '__main__':
    dirname = os.path.join(DIR, 'fudankg-json')
    fname = os.path.join(DIR, 'attributes.txt')

    get_attributes(dirname)
    attr_clustering(fname)
