#coding=utf-8
import nose
import libdata
import json

from nose import with_setup
def setup():  #模块的setup代码
    pass

def teardown(): #模块的teardown代码
    pass

def set_ok():  #只针对test_ok的setup代码
    pass

@with_setup(set_ok)
def test_strip_answer():
    text = u'きみは可爱ね。'
    ret = libdata.strip_good_answer(text)
    if ret["status"] == "ok":
        libdata.print_json(ret)
        assert(ret["status"] != "ok")
    #print text
