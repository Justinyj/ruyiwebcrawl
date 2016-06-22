#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import sys
import collections
import codecs
import datetime
import time

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
from hzlib.libdata import slack_msg

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

KIDS_2W_FILENAME = "raw/kidsfaq2w.json"
KIDS_2W_QUERY_FILENAME = "input/kidsfaq2w.txt"
KIDS_2W_SAMPLE_RESULT_QUESTION = "output/kids_faq_result_question.xls"
KIDS_2W_SAMPLE_RESULT_ANSWER = "output/kids_faq_result_answer.xls"


def read_kidsfaq2w(limit=10):
    # filename = getLocalFile(KIDS_2W_FILENAME)
    # list_json = libfile.file2list(filename)
    # list_query = []
    # for item in list_json:
    #     item = json.loads(item)
    #     q = item["_source"]["question"]
    #     if "@" not in q:
    #         list_query.append(q)
    # libfile.lines2file(list_query, getLocalFile(KIDS_2W_QUERY_FILENAME))
    list_query = libfile.file2list(getLocalFile(KIDS_2W_QUERY_FILENAME))
    print "Length of kidsfaq2w ", len(list_query)

    random.shuffle(list_query)
    return list_query[0: limit if limit<len(list_query) else len(list_query)]

def fetch_detail(worker_id=None, worker_num=None, limit=None, config_index="prod"):
    flag_batch = (worker_id is not None and worker_num is not None and worker_num>1)
    flag_prod = (config_index == "prod")
    flag_slack = (flag_prod and worker_id == 0)

    CONFIG ={
        "local":{
                "batch_id": "zhidao-chat4xl0621-20160621",
                "crawl_http_method": "get",
                "crawl_gap": 5,
                "crawl_use_js_engine": False,
                "crawl_timeout": 10,
                "crawl_http_headers": {},
                "note": "知道搜索，闲聊",
                "debug": True,
    #             "cache_server": "http://52.196.166.54:8000"  #内网IP
    #             "cache_server": "http://52.196.166.54:8000"
                "cache_server": "http://192.168.1.179:8000"
            },
        "prod":{
                "batch_id": "zhidao-chat4xl0621-20160621",
                "crawl_http_method": "get",
                "crawl_gap": 5,
                "crawl_use_js_engine": False,
                "crawl_timeout": 10,
                "crawl_http_headers": {},
                "note": "知道搜索，闲聊",
                "debug": False,
            }

    }
    config = CONFIG[config_index]
    #config = {}
    api = ZhidaoFetch(config)
    list_query = libfile.file2list(getLocalFile(KIDS_2W_QUERY_FILENAME))
    print "Length of kidsfaq2w ", len(list_query)



    ts_start = time.time()
    ts_lap_start = time.time()
    counter = collections.Counter()
    if limit:
        list_query = list_query[:limit]
    print len(list_query)

    if flag_slack:
        slack_msg( u"AWS {}/{}. run {} batch_id: {}, urls: {} debug: {}".format(
            worker_id,
            worker_num,
            config["note"],
            config["batch_id"],
            len(list_query),
            config.get("debug",False)) )

    results = []
    for query in list_query:

        if counter["visited"] % 100 ==0:
            print datetime.datetime.now().isoformat(), counter
        counter["visited"]+=1
        if flag_batch:
            if (counter["visited"] % worker_num) != worker_id:
                counter["skipped_peer"]+=1
                continue


        counter["processed"]+=1
        if counter["processed"] % 1000 == 0:
            if flag_slack:
                slack_msg( "AWS {}/{}. working {}. lap {} seconds. {}".format(
                        worker_id,
                        worker_num,
                        config["batch_id"],
                        int( time.time() - ts_lap_start ),
                        json.dumps(counter) ))
                ts_lap_start = time.time()

        ret = api.search_all(query)
        if config.get("debug"):
            print json.dumps(ret, ensure_ascii=False)

        if not flag_batch and ret:
            for item in ret["items"]:
                #print json.dumps(item, ensure_ascii=False, indent=4, sort_keys=True)
                results.append(item)
                item["query"] = query
                for p in ["source","result_index"]:
                    counter["{}_{}".format(p, item[p])] +=1
                for p in [  "question", "answers"]:
                    if p in item:
                        if not isinstance(item[p], unicode):
                            item[p] = item[p].decode("gb18030")

    if not flag_batch:
        filename_output = getLocalFile("output/kids_faq_sample.xls")
        libfile.writeExcel(results, [ "id", "source", "result_index", "cnt_like",  "cnt_answer", "query", "question_id", "question", "answers"], filename_output)


    duration_sec =  int( time.time() -ts_start )
    print "all done, seconds", duration_sec, duration_sec/counter["visited"], counter

    if flag_slack:
        slack_msg( "AWS {}/{}. done {}. total {} seconds".format(
                worker_id,
                worker_num,
                config["batch_id"],
                duration_sec) )


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

    elif "fetch" == option:
        if len(sys.argv)>3:
            worker_id = int(sys.argv[2])
            worker_num = int(sys.argv[3])
            print "fetch with prefetch"
            fetch_detail(worker_id=worker_id, worker_num=worker_num)
        else:
            print "fetch mono"
            fetch_detail()

    elif "fetch_debug" == option:
        print "fetch_debug mono"
        fetch_detail(limit=100, config_index="local")

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
