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

DIR = '/Users/bishop/百度云同步盘/'

def get_attributes(dirname='fudankg-json'):
    attributes = Counter()

    for f in os.listdir(dirname):
        with open(os.path.join(dirname, f)) as fd:
            for entity, avps in json.load(fd).items():
                for a, v in avps:
                    attributes[a] += 1

    items = sorted(attributes.items(), key=itemgetter(1), reverse=True)

    wfname = os.path.join(DIR, 'attributes.txt')
    with open(wfname, 'w') as fd:
        json.dump(items, fd, ensure_ascii=False, indent=4)


def attr_clustering(fname):
    with open(fname) as fd:
        content = json.load(fd)
    attributes = [i[0] for i in content]
    groups = combination(attributes)

    wfname = os.path.join(DIR, 'attributes_in_groups.txt')
    with open(wfname, 'w') as fd:
        json.dump(groups, fd, ensure_ascii=False, indent=4)
    

if __name__ == '__main__':
    dirname = os.path.join(DIR, 'fudankg-json')
    fname = os.path.join(DIR, 'attributes.txt')

    get_attributes(dirname)
    attr_clustering(fname)
