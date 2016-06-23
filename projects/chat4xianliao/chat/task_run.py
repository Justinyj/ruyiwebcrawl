#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import sys
import collections
import codecs
import datetime
import time
import re

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
import glob
import collections

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

def clean_cmu():
    dirname = getLocalFile("raw/cmu/*.txt")
    #print dirname
    lines = set()
    seq = []
    counter = collections.Counter()
    for filename in glob.glob(dirname):
        counter["files"]+=1
        for line in libfile.file2list(filename):
            zhstr = libdata.extract_zh(line)
            counter["lines"]+=1
            if zhstr and len(zhstr)>1:
                counter["occurs"]+=1
                #print zhstr
                seq.append(zhstr)
                lines.add(zhstr)

    print len(lines)
    filename_output = getLocalFile("output/cmu6w.txt")
    libfile.lines2file(sorted(list(lines)), filename_output)

    print len(seq)
    filename_output = getLocalFile("output/cmu6w_seq.txt")
    libfile.lines2file(seq, filename_output)


LONGQUAN_18W_FILENAME = getLocalFile("raw/xianer_all_question.xlsx")
LONGQUAN_18W_FILENAME_QUESTION = getLocalFile("input/xianer_all_question.txt")

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

def read_longquan18w():

    # test

    data = libfile.readExcel(["count", "question"], LONGQUAN_18W_FILENAME)
    result = set()
    for sheet in data:
        for item in data[sheet]:
            q = clean_longquan_question(item["question"])
            if q and len(q) > 2:
                result.add(q)
    print "Number of longquan question ", len(result)
    libfile.lines2file(result, LONGQUAN_18W_FILENAME_QUESTION)

def clean_longquan_question(question):
    question = question.strip()
    if not question:
        return ""

    if re.compile(ur"^[A-Za-z\*\~\{\}\(\)\[\]\+\?\^\$\"\\\'\|\|\-\.\^\_\d\s,;/:~<>!，。、！？（）＋‘’《》｛｝＊…～★【】“” ｜〈〉︿#％@=&`０１２３４５６７８９：；＜＞＠［］～￥·—『』]+$") \
     .search(question):
        # print question
        return ""

    if re.compile(ur"|善哉|尼玛|释迦牟尼|六根|师兄|观音|菩萨|出家|般若|波罗蜜|修行|方丈|三宝|三藏|菩提| \
    素斋|业障|宗派|五蕴|开悟|参禅|涅槃|慧根|我执|众生|心经|俗家|受戒|龙泉|和尚|法师|佛|禪|禅|丈|淫|寺") \
    .search(question):
        # print question
        return ""

    if re.compile(ur"下一句|馅儿|轮回|出家|诗|僧|阿弥|色即是空|唵|经书|经文|男无|释迦|[念诵].{0,2}经") \
    .search(question):
        # print question
        return ""

    if re.compile(ur"师[叔公妹哥母]|师父|贤二|二贤|师傅").search(question):
        # print question
        return ""

    if re.compile(ur"[\dA-Za-z●☆]").search(question):
        # print question
        return ""

    # question = re.sub(ur'师傅', u'师父', question)
    # question = re.sub(ur'贤二(师父|师傅)|贤二|^你师父|^师父|二贤', u'', question)
    # question = re.sub(ur'问你师父$|问师父', u'问别人', question)
    question = re.sub(ur'|🙏|\.{3,}|\t|\[.{1,2}\]', "", question)
    question = re.sub(ur'/?:[A-Za-z\*\~\{\}\(\)\[\]\+\?\^\$\"\\\'\|\|\-\.\^\_\d,;/:~<>!，。、！？\
    （）＋‘’《》｛｝＊…～★【】“” ｜〈〉︿#％@=&`０１２３４５６７８９：；＜＞＠［］～￥·—『』]{1,4}', "", question)
    question = question.strip()
    question = re.sub(ur".+\s+.+", "，", question)

    if len(question) > 15:
        return ""

    return question.strip()

def fetch_detail(worker_id=None, worker_num=None, limit=None, config_index="prod", filename_input=None):
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
    print filename_input
    if not filename_input:
        print "FATAL "
        return
    else:
        list_query = libfile.file2list(filename_input)
        print "Length of kidsfaq2w ", len(list_query)

    config = CONFIG[config_index]
    #config = {}
    api = ZhidaoFetch(config)



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

        #ret = api.search_all(query)
        ret = api.search_chat_top_n(query, 3 )

        if ret and ret["items"]:
            counter["has_result"] +=1
            counter["total_qa"] += len(ret["items"])
            if config.get("debug"):
                print len(ret["items"]), json.dumps(ret, ensure_ascii=False)
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
        else:
            counter["missing_data"] +=1
            pass

    for item in results:
        item["label"]=""

    job_name = os.path.basename(filename_input).replace(".txt","")
    if flag_batch:
        filename_output = getLocalFile("output/{}.worker_{}.xls".format(job_name, worker_id))
    else:
        filename_output = getLocalFile("output/{}.{}.xls".format(job_name, "all"))
    #libfile.writeExcel(results, [ "id", "source", "result_index", "cnt_like",  "cnt_answer", "query", "question_id", "question", "answers"], filename_output)
    #libfile.writeExcel(results, [ "id","is_good", "match_score", "result_index", "cnt_like",  "cnt_answer", "query", "question", "answers"], filename_output, page_size=5000)
    #print filename_output
    libfile.writeExcel(results, [ "label","query", "answers", "match_score", "question"], filename_output)


    duration_sec =  int( time.time() -ts_start )
    print "all done, seconds", duration_sec, duration_sec/counter["visited"], counter

    if flag_slack:
        slack_msg( "AWS {}/{}. done {}. total {} seconds".format(
                worker_id,
                worker_num,
                config["batch_id"],
                duration_sec) )


def run_chat_realtime(query_filter, query_parser, limit):
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
        """
            python chat/task_run.py fetch input/chat8cmu6w.txt 1 2
        """
        if len(sys.argv)>4:
            filename_input = sys.argv[2]
            worker_id = int(sys.argv[3])
            worker_num = int(sys.argv[4])
            filename_input = getLocalFile(filename_input)
            print "fetch with prefetch"
            fetch_detail(worker_id=worker_id, worker_num=worker_num, filename_input=filename_input)
        else:
            """
                python chat/task_run.py fetch input/chat8cmu6w.txt
            """
            print "fetch mono"
            filename_input = sys.argv[2]
            filename_input = getLocalFile(filename_input)
            fetch_detail(filename_input=filename_input)

    elif "fetch_debug" == option:
        """
            python chat/task_run.py fetch_debug input/chat8cmu6w.txt
        """
        print "fetch_debug mono"
        filename_input = sys.argv[2]
        filename_input = getLocalFile(filename_input)
        fetch_detail(limit=10, config_index="local", filename_input=filename_input)

    elif "clean_cmu" == option:
        clean_cmu()

    elif "read_longquan18w" == option:
        read_longquan18w()

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

        run_chat_realtime(query_filter, query_parser, limit)

    else:
        print "unsupported"

if __name__ == '__main__':
    main()
