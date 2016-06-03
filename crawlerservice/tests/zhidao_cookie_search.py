#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

#从100跳转 http://zhidao.baidu.com/question/584500047.html?qbl=relate_question_1
# urllib.unquote('BAIDUID=F4FA68EF6541217A317954F8E5A83B09:FG=1; Hm_lvt_6859ce5aaf00fb00387e6434e4fcc925=1464845871; Hm_lpvt_6859ce5aaf00fb00387e6434e4fcc925=1464845871; IK_F4FA68EF6541217A317954F8E5A83B09=1; IK_CID_80=1; IK_REFER_QID=100; PMS_JT=%28%7B%22s%22%3A1464846255873%2C%22r%22%3A%22http%3A//zhidao.baidu.com/question/100.html%22%7D%29')
# 'BAIDUID=F4FA68EF6541217A317954F8E5A83B09:FG=1; Hm_lvt_6859ce5aaf00fb00387e6434e4fcc925=1464845871; Hm_lpvt_6859ce5aaf00fb00387e6434e4fcc925=1464845871; IK_F4FA68EF6541217A317954F8E5A83B09=1; IK_CID_80=1; IK_REFER_QID=100; PMS_JT=({"s":1464846255873,"r":"http://zhidao.baidu.com/question/100.html"})'

from __future__ import print_function, division

import hashlib

target = 'f4fa68ef6541217a317954f8e5a83b09'
target = '6859ce5aaf00fb00387e6434e4fcc925'

hash = lambda x: hashlib.md5(x).hexdigest()

source = [
    '100',
    '584500047',
    'http://zhidao.baidu.com/question/584500047.html',
    'http://zhidao.baidu.com/question/100.html',
    'http://zhidao.baidu.com/question/584500047.html?qbl=relate_question_1',
    '1464845871',
    '1464846255873',
    'F4FA68EF6541217A317954F8E5A83B09',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
]

for i in source:
    r1 = hash(i)
    r2 = hash(r1)
    r3 = hash(r2)
    r4 = hash(r3)
    r5 = hash(r4)
    if r1 == target or \
       r2 == target or \
       r3 == target or \
       r4 == target or \
       r5 == target:
       print('find: ', i)
