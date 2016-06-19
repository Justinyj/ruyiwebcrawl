#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import sys
import collections
import codecs
import datetime
import json
import re

def is_question_baike(question):
    if not isinstance(question, unicode):
        question = question.decode("utf-8")

    if not question:
        return False
    question_clean = re.sub(ur"你知道|告诉我|我[国]","", question)
    if re.search(ur"你|我|几点|爸爸|妈妈", question_clean):
        return False
    elif re.search(ur"什么|最|第一|哪|谁|有没有|几|吗|如何|是|有多|[多最][快慢好坏强高少远长老久]|怎么?样?|啥|？",question):
        return True
    elif re.search(ur"百科|距离|历史|介绍|信息",question):
        return True
    else:
        return False


def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename


def test_is_question_baike():

    assert(is_question_baike(None)== False)

    import libfile

    filenames = [
        getTheFile("baike_questions_pos.txt"),
        getTheFile("baike_questions_neg.txt")
    ]
    counter = collections.Counter()
    regex_white1 = ur"你知道|我[国们]";
    regex_black = ur"你|我";
    regex_white2 = ur"什么|最|哪|谁|百科|吗|是|有|多|怎么?样?|啥|如何|距离|历史|介绍|信息|？";
    for filename in filenames:
        print "=====", filename
        lines = libfile.file2list(filename)

        for line in lines:
            if is_question_baike(line):
                actual = "_pos"
            else:
                actual = "_neg"

            if not actual in filename:
                counter["F"] += 1
                print line
            else:
                counter["T"] += 1
    print counter, "error rate", 1.0*counter["F"]/(counter["F"]+counter["T"])


def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "test" == option:
        test_is_question_baike()


if __name__ == "__main__":
    main()
