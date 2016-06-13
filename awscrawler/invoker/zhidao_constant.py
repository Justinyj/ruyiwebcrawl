#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#
# 'http://zhidao.baidu.com/question/234.html', # 其他类似问题
# 'http://zhidao.baidu.com/question/290804898.html', # 专业回答
# 'http://zhidao.baidu.com/question/40418418.html', # 相关专业回答
# 'http://zhidao.baidu.com/question/159240902.html', # 相关专业回答，answer_id 的模式很奇怪
# 'http://zhidao.baidu.com/question/100000721.html', # 类似问题最新采纳
# 'http://zhidao.baidu.com/question/498103598875409004.html', # 只有问题
# 'http://zhidao.baidu.com/question/1049694095758039499.html', # 有一个问题，自己可以回答
# 'http://zhidao.baidu.com/question/75169695.html', # 提问者采纳，网友采纳，类似问题最新采纳同时存在

from __future__ import print_function, division

BATCH_ID = {
    'question': 'zhidao-question-20160606',
    'answer': 'zhidao-answer-20160606',
    'json': 'zhidao-json-20160606',
    'result': 'zhidao-result-20160606'
}

HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1'
}

