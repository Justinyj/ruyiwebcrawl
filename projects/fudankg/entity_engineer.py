#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DIR = '/Users/bishop/百度云同步盘/'

def entity_pure_chinese(fname):
    regchinese = re.compile(u'^[\u4e00-\u9fff]+$')
    pure_chinese = []
    alphanumeric = []

    with open(fname) as fd:
        for line in fd:
            word = line.strip()
            if regchinese.match(word.decode('utf-8')) and len(word.decode('utf-8')) > 1:
                pure_chinese.append(word)
            else:
                alphanumeric.append(word)

    with open(fname+'chinese', 'w') as fd:
        fd.write('\n'.join(pure_chinese))
    with open(fname+'alphanumeric', 'w') as fd:
        fd.write('\n'.join(alphanumeric))


if __name__ == '__main__':
    fname = os.path.join(DIR, 'zgdbk_entities.txt')
    entity_pure_chinese(fname)
