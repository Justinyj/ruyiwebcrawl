#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import xlrd

def read(fname):
    bk = xlrd.open_workbook(fname)
    sh = bk.sheet_by_name("Sheet1")
    nrows = sh.nrows
    ncols = sh.ncols

    result = []
    for i in range(1, nrows):
        row_data = sh.row_values(i)
        question = row_data[0]
        answer = row_data[1]
        url = row_data[2]
        our_question = row_data[3]
        result.append((question, answer, url, our_question))
    return result


def statistics(result):
    zhidao_hit_count = 0
    zhidao_data_hit_count = 0
    count = 0

    for i in result:
        count += 1
        if i[1] == '':
            continue
        if 'zybang.com' in i[2]:
            continue
        zhidao_hit_count += 1

        one_id = re.compile('http://zhidao.baidu.com/question/(\d+).html').search(i[2]).group(1)
        if check_id(one_id) is True:
            zhidao_data_hit_count += 1
            print(one_id)

    print(100 * zhidao_hit_count / count)
    print(100 * zhidao_data_hit_count / count)


def check_id(one_id):
    with open('out.txt', 'r') as out:
        for line in out:
            if one_id.strip() == line.strip():
                return True
    return False

fname = '百科服务对百度知道的测试用例.xlsx'
ret = read(fname)
statistics(ret)

