#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
import random
import requests
from fetch.agents import AGENTS_ALL

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Host': 'zhidao.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1'
}

session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
session.headers = header

def get_cookie_template():
    return ("BAIDUID=F4FA68EF6541217A317954F8E5A83B09:FG=1; IK_CID_82=1;"
            " IK_CID_74=5; Hm_lvt_6859ce5aaf00fb00387e6434e4fcc925=1464845871;"
            " Hm_lpvt_6859ce5aaf00fb00387e6434e4fcc925={now}; "
            "IK_F4FA68EF6541217A317954F8E5A83B09={num}; IK_CID_80=6".format(
                now=int(time.time()),
                num=str(random.random())[2:4]))

def test_question():
  global session
  zhidao_url = 'http://zhidao.baidu.com/question/100.html'
  error_count = 0

  for i, agent in enumerate(AGENTS_ALL):
    session.headers['User-Agent'] = agent
    cookiestr = get_cookie_template()
    cookie = dict(l.split('=', 1) for l in cookiestr.split('; '))
    session.cookies.update(cookie)
    resp = session.get(zhidao_url, timeout=10)
    print('\n', resp.headers['Content-Type'])
    if len(resp.content) < 100000:
      print(resp.status_code, resp.url)
      print(i, agent)
      error_count += 1
      if resp.url == zhidao_url:
        print('url same, still error')
    time.sleep(5)
  print('Error percentage: {}'.format(error_count / i))

def test_api():
    global session
    zhidao_api = 'http://zhidao.baidu.com/question/api/mini?qid=100&rid=769&tag=timeliness'

    for i, agent in enumerate(AGENTS_ALL):
        session.headers['User-Agent'] = agent
        resp = session.get(zhidao_api, timeout=10)
        print(resp.status_code, resp.url)
        time.sleep(3)

test_question()
