#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# http://jadesoul.sinaapp.com/2012/05/29/%E5%AD%97%E7%AC%A6%E5%BD%A2%E5%BC%8F%E7%9A%84md5%E4%B8%B2%E7%9A%84%E5%90%84%E4%B8%AA%E5%AD%97%E6%AF%8D%E5%88%86%E5%B8%83%E5%9D%87%E5%8C%80%E5%90%97/

from __future__ import print_function, division

import hashlib
import math
import random
from collections import defaultdict

alphanumber = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
NUM = 50000

def random_str():
    return alphanumber[int(random.random() * len(alphanumber))]

def gen(func):
    """ {0: ['1', '2'], 1: ['f', '3'], ...}
    """
    hash_obj = func(random_str())
    bit_list = defaultdict(list)

    for i in xrange(NUM):
        hash_obj.update(random_str())
        hashkey = hash_obj.hexdigest()
        for i, bit_key in enumerate(hashkey):
            bit_list[i].append(bit_key)
    return bit_list

def cal_entropy(bit_list):
    for i, lst in bit_list.iteritems():
        frequencies = [lst.count(char_set) / len(lst) for char_set in set(lst)]
        entropy = sum( map(lambda p: -p * math.log(p, 2), frequencies) )
        print(i, entropy)

if __name__ == '__main__':
    bit_list = gen(hashlib.md5)
    cal_entropy(bit_list)

    print('\n')
    bit_list = gen(hashlib.sha1)
    cal_entropy(bit_list)
