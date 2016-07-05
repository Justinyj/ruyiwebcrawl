#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import os
from collections import defaultdict
from datetime import datetime

from hzlib.libfile import read_file_iter, write_file
from filter_lib import regdropbrackets
from to_es import summary, sendto_es, fudan_ea_to_json, send_definition_to_es


DIR = '/home/crawl/Downloads/fudankg_saved'
BATCH = 5000


def load_fudankg_json_data():
    data_def = defaultdict(dict)
    data_attr = defaultdict(dict)

    for f in os.listdir(DIR):
        fname = os.path.join(DIR, f)
        with open(fname) as fd:

            for entity, dic in json.load(fd).iteritems():
                for label, value in dic.iteritems():
                    if label == u'Information':
                        if value == []:
                            continue
                        data_def[entity]['definition'] = value
                        data_def[entity]['category'] = dic[u'Tags'] if u'Tags' in dic else None

                    elif label == u'av pair':
                        data_attr[entity]['category'] = dic[u'Tags'] if u'Tags' in dic else None

                        attr_values = defaultdict(list)
                        for a, v in value:
                            if a == u'中文名':
                                continue
                            if a == u'别名' or a == u'又称':
                                if 'alias' in data_attr[entity]:
                                    data_attr[entity]['alias'].append(v)
                                    data_def[entity]['alias'].append(v)
                                else:
                                    data_attr[entity]['alias'] = [v]
                                    data_def[entity]['alias'] = [v]
                                continue

                            data_attr[entity]['attribute'] = attr_values

    send_definition_to_es(data_def, 'definition', fudan=True)
    send_fudan_attribute_to_es(data_attr)


def send_fudan_attribute_to_es(data):
    eavps = []
    count = 0

    for entity, info in data.iteritems():
        for a, v in info['attribute'].iteritems():
            if 'alias' in info:
                eavps.append( fudan_ea_to_json(entity, a.encode('utf-8'), a.encode('utf-8'), 'attribute', v, info['category'], info['alias']) )
            else:
                eavps.append( fudan_ea_to_json(entity, a.encode('utf-8'), a.encode('utf-8'), 'attribute', v, info['category']) )
            count += 1

        if len(avps) > BATCH:
            sendto_es(pairs)
            eavps = []
            print('{} process {} files.'.format(datetime.now().isoformat(), count))

    if eavps:
        sendto_es(eavps)


load_fudankg_json_data()
