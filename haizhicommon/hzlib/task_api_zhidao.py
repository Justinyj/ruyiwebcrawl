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

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import libfile
import libdata
from api_zhidao import ZhidaoNlp
from api_zhidao import ZhidaoFetch

gcounter = collections.Counter()
def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def getLocalFile(filename):
    return getTheFile("local/"+filename)


def fn_query_filter(line, api_obj, test_expect=None, test_data=None):
    debug = {}
    if api_obj.is_question_baike(line, query_filter=api_obj.query_filter, debug=debug):
        actual = 1
    else:
        actual = 0

    if api_obj.debug:
        #print actual
        if 1 == test_expect and actual == 0:
            for word in set(debug.get("words",set())):
                api_obj.all_words[word] += 1
            #print line, json.dumps(debug["words"], ensure_ascii=False)
            print line, json.dumps([[word, flag] for word, flag in debug.get("words_pos",[])], ensure_ascii=False)
    return actual



def eval_filter(query_filters=[1,3,2], flag_debug=False):
    api = ZhidaoNlp()
    api.debug = flag_debug
    for query_filter in [1,3,2]:
        api.query_filter = query_filter

        if flag_debug:
            api.all_words = collections.Counter()

        filenames = [
            (getLocalFile("baike/baike_questions_pos.human.txt"), 1),
            (getLocalFile("baike/baike_questions_neg.human.txt"), 0)
        ]
        all_words = collections.Counter()

        tests = []
        for filename, expect in filenames:
            print "=====", filename
            entry = {
                "data":libfile.file2list(filename),
                "expect": expect
            }
            tests.append(entry)
            #gcounter["from_{}".format(os.path.basename(filename))] = len(entry["data"])

        target_names = [u"不是", u"是百科"]
        libdata.eval_fn(tests, target_names, fn_query_filter, api)
        print json.dumps(gcounter, indent=4, sort_keys=True)

        if flag_debug:
            for word, cnt in all_words.most_common(20):
                print word, cnt
                pass



def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "eval_filter" == option:
        eval_filter()

    elif "debug_filter" == option:
        eval_filter([2],True)

    elif "test_baike" == option:
        # python hzlib/task_api_zhidao.py test
        api = ZhidaoNlp()
        if len(sys.argv)>2:
            question = sys.argv[1]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[2])
            ret = api.is_question_baike(question, query_filter=query_filter)
            print question, ret, query_filter
        else:
            question = u"那月亮为什么会跟着我走"
            ret = api.is_question_baike(question)
            print question, ret
            assert(not ret)
            question = u"天空为什么是蓝色的"
            ret = api.is_question_baike(question)
            print question, ret
            assert(ret)

    elif "test_chat_realtime" == option:
        # python hzlib/task_api_zhidao.py test
        api = ZhidaoFetch()
        if len(sys.argv)>2:
            question = sys.argv[1]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[2])
            ret = api.search_chat_best(question, query_filter=query_filter)
            print question, query_filter
            libdata.print_json(ret)

        else:
            question = u"你喜欢蓝色么？"
            ret = api.search_chat_best(question)
            print question
            libdata.print_json(ret)

    elif "test_chat_cache" == option:
        # python hzlib/task_api_zhidao.py test

        config = {
				"batch_id": "test-test-20160620",
				"length": 1,
				"crawl_http_method": "get",
				"crawl_gap": 1,
				"crawl_use_js_engine": False,
				"crawl_timeout": 10,
				"crawl_http_headers": {},
				"debug": False,
				"cache_server": "http://192.168.1.179:8000"
			}
        api = ZhidaoFetch(config)
        if len(sys.argv)>2:
            question = sys.argv[1]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[2])
            ret = api.search_chat_best(question, query_filter=query_filter)
            print question, query_filter
            libdata.print_json(ret)

        else:
            question = u"你喜欢蓝色么？"
            ret = api.search_chat_best(question)
            print question
            libdata.print_json(ret)


if __name__ == "__main__":
    main()
