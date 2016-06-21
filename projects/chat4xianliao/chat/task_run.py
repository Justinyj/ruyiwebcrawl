#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import sys
import collections
import codecs
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
# sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

reload(sys)
sys.setdefaultencoding("utf-8")

import downloader
import es
import json
import random

from hzlib import libfile
from hzlib import libdata
from hzlib.api_zhidao import ZhidaoFetch

KIDS_2W_FILENAME = "projects/chat4xianliao/kidsfaq2w.json"
KIDS_2W_QUERY_FILENAME = "projects/chat4xianliao/kidsfaq2w.txt"
KIDS_2W_SAMPLE_RESULT_QUESTION = "projects/chat4xianliao/kids_faq_result_question.xls"
KIDS_2W_SAMPLE_RESULT_ANSWER = "projects/chat4xianliao/kids_faq_result_answer.xls"

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def getLocalFile(filename):
    return getTheFile("../../../local/"+filename)

def read_kidsfaq2w(limit=10):
    filename = getLocalFile(KIDS_2W_FILENAME)
    list_json = libfile.file2list(filename)
    list_question = []
    for item in list_json:
        item = json.loads(item)
        q = item["_source"]["question"]
        if "@" not in q:
            list_question.append(q)

    libfile.lines2file(list_question, getLocalFile(KIDS_2W_QUERY_FILENAME))
    print "Length of kidsfaq2w ", len(list_question)

    random.shuffle(list_question)
    return list_question[0: limit if limit<len(list_question) else len(list_question)]
    # if limit < len(list_question):
    #     return list_question[0:limit]
    # else:
    #     return list_question

def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    config = {}

    agt = ZhidaoFetch(config)
    option= sys.argv[1]

    if "test_chat_realtime" == option:
        query = u"你喜欢蓝色吗？"
        if len(sys.argv)>2:
            query = sys.argv[2]
        query_filter = 2
        if len(sys.argv)>3:
            query_filter = sys.argv[3]
        query_parser = 0
        if len(sys.argv)>4:
            query_parser = sys.argv[4]
        best_item = agt.search_chat_best(query, query_filter=query_filter, query_parser=query_parser)

        print libdata.print_json(best_item)

    elif "run_chat_realtime" == option:

        limit = 1
        if len(sys.argv)>2:
            limit = int(sys.argv[2])

        query_filter = 2
        if len(sys.argv)>3:
            query_filter = sys.argv[3]

        query_parser = 0
        if len(sys.argv)>4:
            query_parser = sys.argv[4]

        data = read_kidsfaq2w(limit)
        print "Length of sample data ",len(data)


        to_write_question = []
        to_write_answer = []

        for query in data:
            top3_item = agt.search_chat_top_n(query, 3, query_filter=query_filter, query_parser=query_parser)
            print libdata.print_json(top3_item)

            if top3_item:
                for key in ["qapair0","qapair1","qapair2"]:
                    if key in top3_item.keys():
                        one_item_question = {
                            "query" : query,
                            "q" : top3_item[key]["question"]
                        }

                        one_item_answer = {
                            "query" : query,
                            "a" : top3_item[key]["answers"]
                        }
                        
                        to_write_question.append(one_item_question)
                        to_write_answer.append(one_item_answer)

                        print libdata.print_json(one_item_question)
                        print libdata.print_json(one_item_answer)
                    else:
                        break

                print "===================================\n"
        libfile.writeExcel(to_write_question, ["query", "q"], getLocalFile(KIDS_2W_SAMPLE_RESULT_QUESTION))
        libfile.writeExcel(to_write_answer, ["query", "a"], getLocalFile(KIDS_2W_SAMPLE_RESULT_ANSWER))
    else:
        print "unsupported"

if __name__ == '__main__':
    main()
