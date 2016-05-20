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
    ret = qichacha.list_person_search(person, limit=4)
    assert type(ret) == dict

def test_search_corporate():
    corporate_list = ['哈药', '哈尔滨']
    ret = qichacha.list_corporate_search(corporate_list, limit=11)
    assert type(ret) == dict

def test_detail():
    name = '天津仁正企业管理有限公司'
    ret = qichacha.crawl_company_detail(name, subcompany=True)
    assert type(ret) == dict

def test_descendant():
    name = '天津仁正企业管理有限公司'
    ret = qichacha.crawl_descendant_company(name)
    import pdb; pdb.set_trace()
    print( json.dumps(ret, ensure_ascii=False, indent=4) )
