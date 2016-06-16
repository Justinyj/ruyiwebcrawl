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

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from parsers.zhidao_parser import *
from hzlib import libfile

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
    return os.path.abspath(os.path.dirname(__file__)).replace("/python/","/local/") +"/"+filename

def getWorkFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/python/","/local/") +"/"+VERSION+"/"+filename

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
        if q_json is None:
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


    def zhidao_search(self, query, page_number=None):
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
            return parse_search_json_v0615(ret)


    def run_query(self, query, max_page):
        self.counter["query"] +=1
        qids_select = set()
        map_search_result_all = {}
        for page_number in range(max_page):
            print "==== page ", page_number, query
            self.counter["page"] +=1

            map_search_result_local = self.zhidao_search(query, page_number)
            #print json.dumps( map_search_result_local, ensure_ascii=False, indent=4, sort_keys=True)
            map_search_result_all.update(map_search_result_local)
            self.counter["q_total"] += len(map_search_result_local)

            for item in map_search_result_local.values():
                #print item
                if item["rtype"] == "recommend" or (item["cnt_like"] >= 3 and item["question_good"]):
                    self.counter["q_good"] +=1
                    qids_select.add(item["qid"])
                    print item["rtype"], item["cnt_like"], item["cnt_answer"] , item['question'], "<----", item['a_summary']
                else:
                    print item["rtype"], item["cnt_like"], item["cnt_answer"] , item['question']
            print datetime.datetime.now().isoformat(), self.counter
        return map_search_result_all
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
                for item in sorted(ret.values(), key= lambda x:x["rank"]):
                    print json.dumps(item, ensure_ascii=False, indent=4, sort_keys=True)
                    results.append(item)
                    item["query"] = line.decode("utf-8")
                    item["id"] = counter["query"]
                    for p in ["rtype","rank"]:
                        counter["{}_{}".format(p, item[p])] +=1
                    for p in [  "question", "a_summary"]:
                        if p in item:
                            if not isinstance(item[p],unicode):
                                item[p] = item[p].decode("gb18030")

        filename_output = filename.replace("human.txt", "xls")
        libfile.writeExcel(results, [ "id","rtype", "rank", "cnt_like",  "cnt_answer", "query", "qid", "question", "a_summary"], filename_output)
        #libfile.writeExcel(results, ["query", "rtype", "cnt_like",  "cnt_answer", "question", "a_summary"], filename_output)
        print counter

def main():
    agt = ZhidaoPrefetch(CONFIG["local"])
    query = u"珠穆朗玛峰"
    query = u"天空为什么是黄的"
    #agt.run_query(query, 1)
    #agt.run_query_batch( getTheFile("seed_entity.human.txt"), 20)
    #agt.run_query_batch( getTheFile("seed_sentence.human.txt"), 1)
    #agt.run_query_batch( getTheFile("seed_class.human.txt"), 40)
    agt.run_test_search_realtime( getTheFile("seed_test0616.human.txt"), 1)

if __name__ == "__main__":
    main()
