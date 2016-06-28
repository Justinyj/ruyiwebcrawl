#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from collections import defaultdict

def prefix_match(word1, word2):
    if word1 == '' or word2 == '':
        return False

    if word1.startswith(word2) or word2.startswith(word1):
        return True
    return False

def postfix_match(word1, word2):
    if word1 == '' or word2 == '':
        return False

    if word1.endswith(word2) or word2.endswith(word1):
        return True
    return False

def combination(items):
    length = len(items)
    matched = []
    groups = defaultdict(list)

    for i in xrange(length):
        if items[i] in matched:
            continue
        for j in xrange(i+1, length):
            if prefix_match(items[i], items[j]) or \
                postfix_match(items[i], items[j]):
                groups[items[i]].append(items[j])
                matched.append(items[j])

    return groups
