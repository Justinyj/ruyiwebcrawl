#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import codecs
import os
import itertools
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from load_alias import get_all_aliases

DIR = '/Users/bishop/百度云同步盘/'


def add_fudan_alias(dirname, fname):
    outfile = os.path.join(dirname, 'zgdbk_entity_with_alias.txt')

    name = os.path.join(dirname, fname)
    with open(name) as fd, codecs.open(outfile, 'w', encoding='utf-8') as wfd:
        for line in fd:
            entity = line.strip().decode('utf-8')
            aliases = get_all_aliases(entity)
            wfd.write(line.strip())
            wfd.write('\t' + '\t'.join(aliases))
            wfd.write('\n')


def human_rule(entity):
    def word_suffix_count():
        counter = collections.Counter()
        input_file = "{}/zgdbk_entities.txt".format(DIR)
        output_file = "{}/lyd_suffix_count.txt".format(DIR)
        with open(input_file, 'r') as f:
            for line in f:
                line = unicode(line.strip(),'utf-8')
                sub1 = line[-1:]
                counter[sub1] += 1
                sub2 = line[-2:]
                counter[sub2] += 1
                sub3 = line[-3:]
                counter[sub3] += 1
        temp = counter.most_common(1000)
        with open(output_file, 'w') as o:
            for t in temp:
                o.write(t[0]+'\t'+str(t[1])+'\n')

    # picked 1000 line from word_suffix_count
    word_list = [u'问题', u'运动', u'县', u'河', u'岛', u'区', u'市',
                 u'自治州', u'城', u'公司', u'技术', u'工程', u'山脉',
                 u'王朝', u'高原', u'研究所', u'共和国', u'古城']
    longer_word_list = [u'股份有限公司', u'运河', u'商城', u'半岛', u'有限公司', u'自然保护区', u'自治县', u'群岛']

    if not isinstance(entity, unicode):
        entity = entity.decode('utf-8')

    for i in itertools.chain(longer_word_list, word_list):
        if entity.endswith(i):
            if i == u'山脉':
                return entity.rstrip(u'脉')
            return entity.rstrip(i)



if __name__ == '__main__':
    add_fudan_alias(DIR, 'zgdbk_entities.txtchinese')
    
