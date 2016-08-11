#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import os

DATA_DIR = '/data/fudankg_saved'

def extract_entities():
    entities = set()
    for f in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, f)) as fd:
            js = json.load(fd)
            entities.update( [i.encode('utf-8') for i in js.keys()] )

    return entities

if __name__ == '__main__':
    with open('fudankg_entities.dump', 'w') as fd:
        fd.write( '\n'.join(extract_entities()) )
