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

sys.path.append(os.path.join(os.path.dirname(__file__),"../"))
sys.path.append(os.path.join(os.path.dirname(__file__),"../../"))
#sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname((os.path.dirname(__file__)[:-1])[:-1])))

import libfile
import libdata
import glob
from api_zhidao import ZhidaoNlp

false_positive = []
false_negative = []
true_positive = []
true_negative = []

gcounter = collections.Counter()
def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename



def fn_classify_0619(line, api, test_expect=None, test_data=None):
    all_detected_skip_words = api.all_detected_skip_words

    detected_skip_words = api.detect_skip_words(line)
    if all_detected_skip_words:
        for word in detected_skip_words:
            all_detected_skip_words[word]+=1

    if len(detected_skip_words) == 0:
        actual = 0
        if test_expect == 1:
            false_positive.append(line + "\t" + u"\t".join(list(detected_skip_words)))
        else:
            true_negative.append(line)
    else:
        actual = 1
        if test_expect == 0:
            false_negative.append(line + "\t" + u"\t".join(list(detected_skip_words)))

    if api.debug:
        if expect != actual:
            print expect, actual, "\n", u"\n".join(list(detected_skip_words))
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
        ( getTheFile("test/test_question_skip_no.human.txt"), 0 ),
#        ( getTheFile("local/baike/baike_questions_pos.human.txt"), 0),
#        [ getTheFile("local/baike/baike_questions_neg.human.txt"), 0 ],
        ( getTheFile("test/test_question_skip_yes.human.txt"), 1 ),
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


def eval_fn():
    api = ZhidaoNlp(debug=False)
    filenames = [
        ( getTheFile("test/test_question_skip_yes.human.txt"), 1 ),
        # ( getLocalFile("chat4xianliao/chat/input/xianer_all_question.txt"), 0 ),
        ( getTheFile("test/test_question_skip_no.human.txt"), 0 ),
        ( getTheFile("test/test_ask_baike_all.human.txt"), 0 ),
        ( getTheFile("test/test_ask_chat_all.human.txt"), 0 ),
    ]
    tests = []
    for filename, expect in filenames:
        entry = {
            "data":libfile.file2list(filename),
            "expect": expect
        }
        tests.append(entry)
        gcounter["from_{}".format(os.path.basename(filename))] = len(entry["data"])

    target_names = [u"正常", u"敏感词"]
    all_detected_skip_words = collections.Counter()
    setattr(api, "all_detected_skip_words", all_detected_skip_words)
    libdata.eval_fn(tests, target_names, fn_classify_0619, api)

    libfile.lines2file(false_positive, getTheFile("local/skip_words/chat8xianer12w_test_false_positive.txt"))
    libfile.lines2file(false_negative, getTheFile("local/skip_words/chat8xianer12w_test_false_negative.txt"))
    libfile.lines2file(libdata.items2sample(true_negative, 1500 if len(true_negative)>1500 else len(true_negative)), \
    getTheFile("local/skip_words/chat8xianer12w_test_true_negative.txt"))
    print json.dumps(gcounter, ensure_ascii=False),"\n\n------ all done"

def removeLen1Word(words):
    new_words = set()
    for word in words:
        if len(word) > 1:
            new_words.add(word)
    return new_words

def clean_skip_words_all():
    filepath_skip_words_all_new = getTheFile("local/skip_words/skip_words_all_new.human.txt")
    filepath_skip_words_all_auto = getTheFile("localskip_words/test_question_all.auto.txt")

    skip_words_all_new = libfile.file2list(filepath_skip_words_all_new)


    to_remove = set()
    for i in range(0,len(skip_words_all_new)):
        for j in range(i+1,len(skip_words_all_new)):
            if skip_words_all_new[i] in skip_words_all_new[j]:
                to_remove.add(skip_words_all_new[j])
            elif skip_words_all_new[j] in skip_words_all_new[i]:
                to_remove.add(skip_words_all_new[i])
    print "to remove ", len(to_remove)
    libfile.lines2file(sorted(list(to_remove)), getTheFile("local/skip_words/skip_words_all_to_remove.txt"))

    skip_words_all_new = set(skip_words_all_new)
    skip_words_all_new.difference_update(to_remove)
    print "skip_words_all_new after removing to_remove", len(skip_words_all_new)

    skip_words_all_auto = libfile.file2list(filepath_skip_words_all_auto)
    skip_words_all_auto = set(skip_words_all_auto)

    print "skip_words_all_new ", len(skip_words_all_new)
    print "skip_words_all_auto ", len(skip_words_all_auto)

    skip_words_all_new = removeLen1Word(skip_words_all_new)
    skip_words_all_auto = removeLen1Word(skip_words_all_auto)

    print "skip_words_all_new after remove len 1", len(skip_words_all_new)
    print "skip_words_all_auto after remove len 1", len(skip_words_all_auto)

    skip_words_all_core = skip_words_all_new.intersection(skip_words_all_auto)
    skip_words_all_new.difference_update(skip_words_all_core)

    print "skip_words_all_core ", len(skip_words_all_core)

    api = ZhidaoNlp(debug=True)
    skip_words_all_diff = set()
    for word in skip_words_all_new:
        detected_skip_words = api.detect_skip_words(word, skip_words_all_core)
        if len(detected_skip_words) == 0:
            skip_words_all_diff.add(word)
    print "skip_words_all_diff ", len(skip_words_all_diff)

    libfile.lines2file(sorted(list(skip_words_all_core)), getTheFile("local/skip_words/skip_words_all_core.txt"))
    libfile.lines2file(sorted(list(skip_words_all_diff)), getTheFile("local/skip_words/skip_words_all_diff.txt"))

def export_skip_words():
    lines = set()
    lines = libfile.file2set(getTheFile("model/skip_words_all.human.txt"))
    lines.difference_update( libfile.file2set(getTheFile("model/skip_words_all_no.human.txt")) )
    libfile.lines2file(sorted(list(lines)), getTheFile("model/skip_words_x_all.auto.txt"))

    lines.update( libfile.file2set(getTheFile("model/skip_words_all_ext.human.txt")) )
    libfile.lines2file(sorted(list(lines)), getTheFile("model/skip_words_x_nlp.auto.txt"))

def test(text):
    api = ZhidaoNlp(debug=True)
    ret = api.detect_skip_words(text)
    print json.dumps(list(ret), ensure_ascii=False, indent=4)

def main():

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "eval_fn" == option:
        eval_fn()

    elif "test" == option:
        if len(sys.argv)>2:
            sentence = sys.argv[2]
        test(sentence)

    elif "learn" == option:
        learn_skip_words_0619()

    elif "export" == option:
        export_skip_words()

    elif "clean_skip_words_all" == option:
        clean_skip_words_all()


if __name__ == "__main__":
    main()
    print json.dumps(gcounter, ensure_ascii=False, indent=4, sort_keys=True),"\n\n------ all done"
