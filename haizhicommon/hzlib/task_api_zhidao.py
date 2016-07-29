#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 2016-07-01  测试 609 百科类问题
# 543 最优   89%
#	361 正确  59%正确
#	67 错误   10%
#	115 存疑，18%  不完整，应该落入其他领域服务  （对错各半）
#21 问题敏感词 （3%）

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
    debug_item = {}
    if api_obj.is_question_baike(line, query_filter=api_obj.query_filter, debug_item=debug_item):
        actual = 1
    else:
        actual = 0

    if api_obj.debug:
        #print actual
        if 1 == test_expect and actual == 0:
            for word in set(debug_item.get("words",set())):
                api_obj.all_words[word] += 1
            #print line, json.dumps(debug_item["words"], ensure_ascii=False)
            print line, json.dumps([[word, flag] for word, flag in debug_item.get("words_pos",[])], ensure_ascii=False)
    return actual


# def load_good_qa():
# 	EXCEL_FIELDS_ONE = ["note", "q","a"]
#
#
#
# 	qa = {}
# 	for filename in glob.glob(pathexpr):
# 		print filename
# 		tests = libfile.readExcel(EXCEL_FIELDS_ONE, filename, start_row=1).values()[0]
# 		for row in tests.values()[0]:
#             rowid = u"{}###{}".format(row["q"],row["a"])
# 			qa[rowid] = row["note"]


def eval_filter(query_filters=[1,3,2], flag_debug=False):
    api = ZhidaoNlp()
    api.debug = flag_debug
    for query_filter in [1,3,2]:
        api.query_filter = query_filter

        if flag_debug:
            api.all_words = collections.Counter()

        filenames = [
            (getLocalFile("baike/baike_questions_pos.human.txt"), 1),
            (getLocalFile("baike/baike_questions_neg.human.txt"), 0),
            (getLocalFile("baike/baike_questions_chat.human.txt"), 0),
            (getTheFile("test/test_ask_baike_all.human.txt"), 1),
            (getTheFile("test/test_ask_chat_all.human.txt"), 0),
        ]
        all_words = collections.Counter()

        tests = []
        all_query = set()
        for filename, expect in filenames:
            print "=====", filename
            entry = {
                "data":libfile.file2list(filename),
                "expect": expect
            }
            temp = set(entry["data"])
            temp.difference_update(all_query)
            entry["data"] = list(temp)
            all_query.update(entry["data"])
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

    elif "test_is_baike_realtime" == option:
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
            question = sys.argv[2]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[3])
            print question, query_filter
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
            question = sys.argv[2]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[3])
            ret = api.search_chat_best(question, query_filter=query_filter)
            print question, query_filter
            libdata.print_json(ret)

        else:
            question = u"你喜欢蓝色么？"
            ret = api.search_chat_best(question)
            print question
            libdata.print_json(ret)


    elif "test_baike_realtime" == option:
        # python hzlib/task_api_zhidao.py test_baike_realtime
        api = ZhidaoFetch()
        if len(sys.argv)>2:
            question = sys.argv[2]
            query_filter =2
            if len(sys.argv)>3:
                query_filter = int(sys.argv[3])
            print question, query_filter
            ret = api.search_baike_best(question, query_filter=query_filter)
            print question, query_filter
            libdata.print_json(ret)

        else:
            question = u"严重贫血怎么办"
            question = u"天空是什么颜色的？"
            ret = api.search_baike_best(question, keep_result=True)
            print question
            libdata.print_json(ret)

    elif option.startswith("test_baike_cache"):
        # python hzlib/task_api_zhidao.py test_baike_cache
        print "========"
        config = {
				"batch_id": "test-test-20160620",
				"length": 1,
				"crawl_http_method": "get",
				"crawl_gap": 1,
				"crawl_use_js_engine": False,
				"crawl_timeout": 10,
				"crawl_http_headers": {},
				"debug": True,
				"cache_server": "http://192.168.1.179:8000"
			}
        api = ZhidaoFetch(config)
        if option == "test_baike_cache_one":
            #question = u"你喜欢蓝色么？"
            question = u"天空是什么颜色的？"
            question = u"掏粪男孩就是指TFboys吗?"
            question = u"爱因斯坦是谁"
            if len(sys.argv)>2:
                question = sys.argv[2]
            ret = api.search_baike_best(question)
            libdata.print_json(ret)
            print question
        else:
            filename_question = sys.argv[2]
            questions = libfile.file2list(filename_question)

            if questions:
                filename =  u"{}.temp".format(filename_question)
                libfile.lines2file(sorted(list(questions)), filename)

            print len(questions)
            results = []
            for question in questions:
                query_filter =2
                if len(sys.argv)>3:
                    query_filter = int(sys.argv[3])
                debug_item = {}
                ret = api.search_baike_best(question, query_filter=query_filter, debug_item=debug_item)
                print question, query_filter
                #libdata.print_json(ret)
                if not ret:
                    debug_item["best"] = u"异常"
                    debug_item["query"] = question
                    results.append(debug_item)

                elif not ret.get("items_all",[]):
                    debug_item["query"] = question
                    debug_item["best"] = u"无结果"
                    results.append(debug_item)

                else:
                    for item in ret.get("items_all",[]):
                        item["query"] = question
                        results.append(item)
                        if item["id"] == ret.get("best_qapair",{}).get("id"):
                            item["best"] = u"最优"
                        else:
                            item["best"] = u""


            filename = getLocalFile("temp/test_baike_cache.{}.xls".format(os.path.basename(filename_question)))
            fields = [u"标注", "best", "debug_note", "query", "answers", "match_score", "cnt_like", "cnt_answer", "question", "id", "answers_raw", "question_content"]
            libfile.writeExcel(results, fields, filename)



    elif "test_jieba" == option:
        api = ZhidaoNlp()
        question = sys.argv[2]
        if not isinstance(question, unicode):
            question = question.decode("utf-8")

        temp = api.cut_text( question )
        print json.dumps(list(temp), ensure_ascii=False)

        temp = api.pseg.cut( question )
        for word, pos in temp:
            print word, pos

if __name__ == "__main__":
    main()
