#coding=utf-8
import nose
import libdata
import json
import libnlp
import sys

from nose import with_setup
def setup():  #模块的setup代码
    pass

def teardown(): #模块的teardown代码
    pass

def set_ok():  #只针对test_ok的setup代码
    pass

@with_setup(set_ok)
def test_skip_words():
    lib = libnlp.SimpleNlp()
    skip_words = lib.detect_skip_words(u"你好吗")
    assert(len(skip_words)==0)
    skip_words = lib.detect_skip_words(u"你大爷的")
    assert(len(skip_words)>0)
    #print text


def run_skip_words(text):
    lib = libnlp.SimpleNlp()
    skip_words = lib.detect_skip_words(text)
    print "test_skip_words: {} | text: {} | skip:".format( len(skip_words)>0, text), json.dumps(skip_words, ensure_ascii=False)

def main():
    #print sys.argv

    if len(sys.argv)<2:
        "please provide option"
        return

    option= sys.argv[1]

    if "run_skip_words" == option:
        if len(sys.argv)>2:
            question = sys.argv[2]
            run_skip_words(question)


if __name__ == "__main__":
    main()
