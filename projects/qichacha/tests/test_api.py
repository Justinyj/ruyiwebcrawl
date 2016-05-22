#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from core.qichacha import Qichacha

qichacha = Qichacha(batch_id='qichacha', groups='哈药')

def test_search_person():
    person = '吴志军'
    ret = qichacha.list_person_search(person, limit=10)
    assert type(ret) == dict

def test_search_corporate():
    corporate_list = ['哈药', '哈尔滨']
    ret = qichacha.list_corporate_search(corporate_list, limit=10)
    assert type(ret) == dict

def test_search_corporate_count():
    corporate_list = ['哈尔滨','哈尔滨红肠很好吃']
    ret = qichacha.list_corporate_search_count(corporate_list)
    assert type(ret) == dict

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
