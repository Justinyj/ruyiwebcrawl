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
import time

sys.path.append(os.path.abspath("../"))
sys.path.append(os.path.abspath("../../"))
#sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname((os.path.dirname(__file__)[:-1])[:-1])))

import libfile
import libdata
import glob
from api_zhidao import ZhidaoNlp


gcounter = collections.Counter()
def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename


def fn_classify_0619(line, api, test_expect=None, test_data=None):
    skip_words_all = api.skip_words_all
    all_detected_skip_words = api.all_detected_skip_words

    if api.debug:
        print len(skip_words_all)
    detected_skip_words = api.detect_skip_words(line, skip_words_all)
    if all_detected_skip_words:
        for word in detected_skip_words:
            all_detected_skip_words[word]+=1

    if len(detected_skip_words) == 0:
        actual = 0
    else:
        actual = 1

    if api.debug:
        print actual, "\n", u"\n".join(list(detected_skip_words))
    return actual

def learn_skip_words_0619():
    api = ZhidaoNlp(debug=True)

    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ load all raw",
    skip_words_raw = collections.Counter()
    filenames = glob.glob( getTheFile("local/skip_words/skip_words_*.raw.txt") )
    for filename in filenames:
        for phrase in libfile.file2list(filename):
            gcounter["from_{}".format(os.path.basename(filename))] += 1
            skip_words_raw[phrase]+=1
    gcounter["skip_words_raw_loaded"] = len(skip_words_raw)

    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ generate clean",
    skip_words_clean = collections.Counter()
    for phrase in skip_words_raw:
        temp = api.cut_text(phrase)
        for word in temp:
            skip_words_clean[word] += skip_words_raw[phrase]
    gcounter["skip_words_clean"] = len(skip_words_clean)


    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ estimate raw outside clean"
    skip_words_raw_diff = set(skip_words_raw)
    skip_words_raw_diff.difference_update(skip_words_clean)
    for phrase in libdata.items2sample(skip_words_raw_diff):
        print phrase, skip_words_raw[phrase]
    gcounter["skip_words_raw_diff"] = len(skip_words_raw_diff)


    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ load not clean "
    not_skip_words_clean = set()
    filenames = glob.glob( getTheFile("model/skip_words_no.human.txt") )
    for filename in filenames:
        for line in libfile.file2list(filename):
            if line not in not_skip_words_clean:
                gcounter["from_{}".format(os.path.basename(filename))] += 1
                not_skip_words_clean.add(line)
    gcounter["not_skip_words_clean_loaded"] = len(not_skip_words_clean)


    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ filter clean with not "
    skip_words_all = set( skip_words_clean )
    skip_words_all.difference_update(not_skip_words_clean)
    gcounter["skip_words_all"] = len(skip_words_all)
    filename = getTheFile("local/skip_words/test_question_all.auto.txt")
    libfile.lines2file(sorted(list(skip_words_all)), filename)


    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ eval performance"
    filenames = [
        ( getTheFile("local/skip_words/test_question_skip_no.human.txt"), 0 ),
#        ( getTheFile("local/baike/baike_questions_pos.human.txt"), 0),
#        [ getTheFile("local/baike/baike_questions_neg.human.txt"), 0 ],
        ( getTheFile("local/skip_words/test_question_skip_yes.human.txt"), 1 ),
    ]
    all_detected_skip_words = collections.Counter()
    counter = collections.Counter()
    tests = []
    for filename, expect in filenames:
        entry = {
            "data":libfile.file2list(filename),
            "expect": expect
        }
        tests.append(entry)
        gcounter["from_{}".format(os.path.basename(filename))] = len(entry["data"])

    target_names = [u"正常", u"敏感词"]
    setattr(api, "all_detected_skip_words", all_detected_skip_words)
    setattr(api, "skip_words_all", skip_words_all)
    libdata.eval_fn(tests, target_names, fn_classify_0619, api)


    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ all done"

def test(query):
    api = HzNlp(debug=True)
    print api.skip
    print "test"


def main():

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "test" == option:
        query = sys.argv[2]
        fn_classify_0619(query, api)

    elif "learn" == option:
        learn_skip_words_0619()




if __name__ == "__main__":
    main()
