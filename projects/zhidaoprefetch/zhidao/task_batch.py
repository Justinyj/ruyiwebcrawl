#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import sys
import collections
import codecs
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'parser')))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'parser')))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'parser')))

reload(sys)
sys.setdefaultencoding("utf-8")
import downloader
import es
import hzlib
import jieba

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from parsers.zhidao_parser import *
from hzlib import libfile
from zhidao_fetch import search_zhidao_best

#############
# config
CONFIG_T = {
     "batch_ids": {
         "search": "zhidao-search-20160614",
         "question": "zhidao-question-20160614",
         "answer": "zhidao-answer-20160614",
         "json": "zhidao-json-20160614"
     },
     "cache_server": "http://52.192.116.149:8000",
     "http_headers": {
         "Host": "zhidao.baidu.com"
     },
     "crawler": {
         "gap": 3,
         "timeout": 10,
         "encoding": "gb18030",
         "error_check": True
     }
}

CONFIG = {
    "prod": CONFIG_T,
    "local": CONFIG_T,
}
CONFIG["local"]["cache_server"] = "http://192.168.1.179:8000"
#     "cache_server": "http://52.192.116.149:8000",

VERSION ='v20160526'

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getWorkFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+VERSION+"/"+filename

class ZhidaoPrefetch(object):

    def __init__(self, config):
        self.config = config
        self.counter = collections.Counter()
        self.cache = Cache(self.config["batch_ids"]["json"], self.config["cache_server"])
        self.downloader = DownloadWrapper(self.config["cache_server"], self.config["http_headers"])

    def is_debug(self):
        return self.config.get("debug", False)

    def zhidao_results(self, qids):
        q_jsons = []
        for qid in qids:
            q_json = self.zhidao_question(qid)
            if q_json is False:
                continue
            q_json["list_answers"] = []

            for rid in q_json["answer_ids"][:3]:
                a_json = self.zhidao_answer(qid, rid)
                if a_json is False:
                    continue
                q_json["list_answers"].append(a_json)

            q_jsons.append(q_json)
        return q_jsons


    def zhidao_question(self, qid):
        question_url = "http://zhidao.baidu.com/question/{}.html".format(qid)
        if self.is_debug():
            print question_url
        ret = self.downloader.downloader_wrapper(
                        question_url,
                        self.config["batch_ids"]["question"],
                        self.config["crawler"]["gap"],
                        timeout=self.config["crawler"]["timeout"],
                        encoding=self.config["crawler"]["encoding"])
        if ret is False:
            return False
        q_json = generate_question_json(qid, ret)
        if q_json is None or q_json == {}:
            return False
        success = self.cache.post(question_url, q_json)
        return q_json


    def zhidao_answer(self, qid, rid):
        answer_url = ("http://zhidao.baidu.com/question/api/mini?qid={}"
                      "&rid={}&tag=timeliness".format(qid, rid))

        #print self.config["crawler"]
        if self.is_debug():
            print answer_url
        ret = self.downloader.downloader_wrapper(
                    answer_url,
                    self.config["batch_ids"]["answer"],
                    self.config["crawler"]["gap"],
                    timeout=self.config["crawler"]["timeout"],
                    encoding=self.config["crawler"]["encoding"])
        if ret is False:
            return False
        try:
            a_json = generate_answer_json(ret)
        except:
            return False

        success = self.cache.post(answer_url, a_json)
        return a_json


    def zhidao_search(self, query, page_number=None, start_result_index=0):
        if isinstance(query, unicode):
            query = query.encode("utf-8")

        if page_number is None or page_number == 0:
            query_url = "http://zhidao.baidu.com/search/?word={}".format( urllib.quote(query) )
        else:
            query_url = "http://zhidao.baidu.com/search/?pn={}&word={}".format( page_number*10, urllib.quote(query) )
        if self.is_debug():
            print query_url
        # query_url = "http://zhidao.baidu.com/search?word={}".format(quote_word)

        #print query
        #print query_url
        ret = self.downloader.downloader_wrapper(
                query_url,
                self.config["batch_ids"]["search"],
                self.config["crawler"]["gap"],
                timeout=self.config["crawler"]["timeout"],
                encoding=self.config["crawler"]["encoding"],
                refresh=False)
        # resp.headers: "content-type": "text/html;charset=UTF-8",
        # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
        if ret is False:
            return False
        else:
            return parse_search_json_v0615(ret, start_result_index=start_result_index)


    def run_query(self, query, max_page):
        self.counter["query"] +=1
        qids_select = set()
        result_all = []
        for page_number in range(max_page):
            print "==== page ", page_number, query
            self.counter["page"] +=1

            result_local = self.zhidao_search(query, page_number, len(result_all) )
            #print json.dumps( result_local, ensure_ascii=False, indent=4, sort_keys=True)
            result_all.extend(result_local)
            self.counter["q_total"] += len(result_local)

            for item in result_local:
                item["query"] = query
                if type(query) != unicode:
                    item["query"] = query.decode("utf-8")
                #print item
                if item["source"] == "recommend" or (item["cnt_like"] >= 3):
                    self.counter["q_good"] +=1
                    qids_select.add(item["question_id"])
                    print item["source"], item["cnt_like"], item["cnt_answer"] , item['question'], "<----", item['answers']
                else:
                    print item["source"], item["cnt_like"], item["cnt_answer"] , item['question']
            print datetime.datetime.now().isoformat(), self.counter
        return result_all
            #qajson = self.zhidao_results(qids_select)
        #print json.dumps(qajson, ensure_ascii=False, indent=4)

    def run_query_entity(self):
        filename = getTheFile("seed_entity.human.txt")
        with codecs.open(filename) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip()
                if not line:
                    continue

                self.run_query(line, 10)

    def run_query_batch(self, filename, limit):
        with codecs.open(filename) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip()
                if not line:
                    continue
                self.run_query(line, limit)


    def run_gen_url_search_realtime(self, filename):
        lines = libfile.file2list(filename)
        visited = set()
        for line in sorted(lines):
            for query_parser in [0]:
                query_url, qword = zhidao_fetch.get_search_url_qword(line, query_parser=query_parser)

                if query_url in visited:
                    continue
                visited.add(query_url)
                print qword, query_url

        print len(visited)
        filename_output = getLocalFile(os.path.basename(filename.replace("human.txt", "_urls.txt")))
        libfile.lines2file(sorted(list(visited)), filename_output)

  def run_test_search_realtime(self, filename, limit):
        results = []
        counter = collections.Counter()

        with codecs.open(filename) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip()
                if not line:
                    continue
                ret = self.run_query(line, limit)
                counter["query"] +=1
                for item in ret:
                    #print json.dumps(item, ensure_ascii=False, indent=4, sort_keys=True)
                    results.append(item)
                    for p in ["source","result_index"]:
                        counter["{}_{}".format(p, item[p])] +=1
                    for p in [  "question", "answers"]:
                        if p in item:
                            if not isinstance(item[p],unicode):
                                item[p] = item[p].decode("gb18030")

        filename_output = getLocalFile(os.path.basename(filename.replace("human.txt", "xls")))
        libfile.writeExcel(results, [ "id", "source", "result_index", "cnt_like",  "cnt_answer", "query", "question_id", "question", "answers"], filename_output)
        #libfile.writeExcel(results, ["query", "source", "cnt_like",  "cnt_answer", "question", "answers"], filename_output)
        print counter

    def run_get_best_search_realtime(self, filename):
        results = []
        counter = collections.Counter()

        lines = libfile.file2list(filename)
        for query_parser in [0]:
            for line in sorted(lines):
                cnt_label = "query_{}".format(query_parser)
                if counter[cnt_label] % 10 == 0:
                    print datetime.datetime.now().isoformat(), counter[cnt_label], line
                counter[cnt_label] +=1

                ret_one = search_zhidao_best(line, query_filter=0, query_parser=query_parser)
                if ret_one:
                    item = ret_one["best_qapair"]
                    for p in ["query"]:
                        item[p] = ret_one[p]
                    #print json.dumps(item, ensure_ascii=False, indent=4, sort_keys=True)
                    results.append(item)
                    for p in ["source","result_index"]:
                        counter["{}_{}".format(p, item[p])] +=1
                    for p in [  "question", "answers"]:
                        if p in item:
                            if not isinstance(item[p],unicode):
                                item[p] = item[p].decode("gb18030")

        filename_output = getLocalFile(os.path.basename(filename.replace("human.txt", "xls")))
        libfile.writeExcel(results, [ "id", "source", "result_index", "cnt_like",  "cnt_answer", "query", "question_id", "question", "answers"], filename_output)
        #libfile.writeExcel(results, ["query", "source", "cnt_like",  "cnt_answer", "question", "answers"], filename_output)
        print counter


def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    agt = ZhidaoPrefetch(CONFIG["prod"])
    option= sys.argv[1]
    if "query" == option:
        query = u"天空为什么是蓝色的？"
        if len(sys.argv)>2:
            query = sys.argv[2]
        agt.run_query(query, 1)
    elif "batch_entity" == option:
        agt.run_query_batch( getTheFile("seed_entity.human.txt"), 20)
    elif "batch_sentence" == option:
        agt.run_query_batch( getTheFile("seed_sentence.human.txt"), 1)
    elif "batch_class" == option:
        agt.run_query_batch( getTheFile("seed_class.human.txt"), 40)
    elif "realtime_xls" == option:
        agt = ZhidaoPrefetch(CONFIG["local"])
        agt.run_test_search_realtime( getTheFile("seed_test0616.human.txt"), 1)
    elif "realtime_best" == option:
        worker_id = 0
        if len(sys.argv)>2:
            worker_id = int(sys.argv[2])
        worker_num = 1
        if len(sys.argv)>3:
            worker_num = int(sys.argv[3])
        #agt.run_get_best_search_realtime(getTheFile("seed_test0616.human.txt"))

        agt.run_get_best_search_realtime(getTheFile("seed_sentence.human.txt"))
    elif "realtime_url" == option:
        agt.run_gen_url_search_realtime(getTheFile("seed_sentence.human.txt") )

    else:
        print "unsupported"

if __name__ == '__main__':
    main()
