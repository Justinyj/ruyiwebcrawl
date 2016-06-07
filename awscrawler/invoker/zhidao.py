#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from awscrawler import post_job


BATCH_ID = {
    'question': 'zhidao-question-20160606',
    'answer': 'zhidao-answer-20160606',
    'json': 'zhidao-json-20160606',  #
    'result': 'zhidao-result-20160606'  # 合并后
}

def load_urls(fname):
    with open(fname) as fd:
        return [i.strip() for i in fd if i.strip() != '']

filename = 'userful_zhidao_urls.txt'
urls = load_urls(filename)
post_job(BATCH_ID['question'], 'get', 3, urls)
post_job(BATCH_ID['answer'], 'get', 3, [], len(urls) * 3)
start_up_ec2(10, BATCH_ID['question'].split('-', 1)[0])
