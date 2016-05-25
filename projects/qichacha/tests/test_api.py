#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
import json
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

from core.qichacha import Qichacha

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

filename = getTheFile("../config/conf.179.json")
with open(filename) as f:
    config = json.load(f)['test']
qichacha = Qichacha(config, batch_id='qichacha', groups='哈药')

def test_search_person():
    person = '吴志军'
    ret = qichacha.list_person_search(person, limit=10)
    assert type(ret) == dict

def test_search_corporate():
    corporate_list = ['哈药', '哈尔滨']
    ret = qichacha.list_corporate_search(corporate_list, limit=10)
    assert type(ret) == dict

def test_search_corporate_count():
    keyword_list = ['哈尔滨','哈尔滨红肠很好吃']
    for keyword in keyword_list:
        ret = qichacha.get_keyword_search_count(keyword, 2)
        assert type(ret) == int

def test_detail():
    name = '天津仁正企业管理有限公司'
    ret = qichacha.crawl_company_detail(name, subcompany=True)
    assert type(ret) == dict

def test_descendant():
    name = '上海新微科技发展有限公司'
    ret = qichacha.crawl_descendant_company(name)
    assert type(ret) == dict

def test_ancestors():
    name = '上海菊园物联网科技服务有限公司'
    ret = qichacha.crawl_ancestors_company(name)
    assert type(ret) == dict
