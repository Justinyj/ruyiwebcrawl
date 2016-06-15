# -*- coding: utf-8 -*-


from __future__ import print_function, division
import json
import sys
import os
from parsers.zhidao_parser import *
reload(sys)
sys.setdefaultencoding('utf-8')

def test_parse_title():
    content='<title>123_百度知道</title>'
    ret = parse_page_title(content)
    assert ret==u'123_百度知道'
    assert type(ret)== str

    with open('examples/question1.html','r') as f:
    	content=f.read().decode('utf-8')
    ret = parse_page_title(content)
    assert ret==u'重庆周遍比较特色的旅游。'

def test_search():
    with open('examples/zhidaosearch1.html','r') as f:
    	content=f.read().decode('utf-8')
    ret= zhidao_search_questions(content)
    assert ret==['421299483','24164629']

    with open('examples/zhidaosearch2.html','r') as f:
        content=f.read().decode('utf-8')
    ret= zhidao_search_questions(content)
    assert ret==['363204963']
