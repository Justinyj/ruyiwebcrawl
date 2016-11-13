#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
from core.qichacha import Qichacha

def read_accounts():
    accounts = []
    with open('config/conf.fs.json') as fd:
        jsn = json.load(fd)
        config = jsn[u'vip']
        return config

        for name_pass, cookie in jsn[u'vip'][u'COOKIES'].iteritems():
            username, password = name_pass.split(u'_')
            accounts.append(username, password, cookie)
    return accounts


def init():
    config = read_accounts()
    # 在业
    list_url10 = 'http://www.qichacha.com/search?key={key}&index={index}&province={province}statusCode=10&sortField=registcapi&isSortAsc=false&p={page}'
    # 存续
    list_url20 = 'http://www.qichacha.com/search?key={key}&index={index}&province={province}statusCode=20&sortField=registcapi&isSortAsc=false&p={page}'
    q10 = Qichacha(config, batch_id='qichacha1111', request=True, list_url=list_url10)
    q10.list_keyword_search(u'中药饮片', [12], 5000)

#    q20 = Qichacha(config, batch_id='qichacha1111', request=True, list_url=list_url10)
#    q20.list_keyword_search(u'中药饮片', [12], 5000)

if __name__ == '__main__':
    init()
