#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  curl -XDELETE -u es_ruyi:ruyiruyies http://nlp.ruyi.ai:9200/ruyiwebcrawl_zhidaoqa_0626
# http://api.ruyi.ai/ruyi-nlp/cache/clear?prefix=prod&suffix=answers


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
import json
import random
import glob
import collections

from es import es_api
from hzlib import libfile
from hzlib import libdata
from hzlib.api_zhidao import ZhidaoNlp

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

gcounter = collections.Counter()

ES_DATASET_CONFIG ={
    "chat8cmu6w":
    {   "description":"知道短问答",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"default",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "chat8xianer12w":
    {   "description":"知道短问答 chat8xianer12w",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"chat8xianer12w",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "zhidao_question":
    {   "description":"知道短问答 zhidao_question",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"zhidao_question",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "zhidao_query":
    {   "description":"知道短问答 zhidao_query",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"zhidao_query",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "xianer7w_rewrite":
    {   "description":"知道短问答 xianer7w_rewrite",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"xianer7w_rewrite",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "baike_qa":
    {   "description":"知道百科问答 baike_qa",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"baike_qa_0707",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "qa0708chat10k":
    {   "description":"知道10K qa0708chat10k",
        "es_index":"ruyiwebcrawl_zhidaoqa_0626",
        "es_type":"qa0708chat10k",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "xianer12w_test":
        {   "description":"贤二短问答",
            "es_index":"ruyiwebcrawl_zhidaoqa_0626",
            "es_type":"xianer12w_test",
            "filepath_mapping": getTheFile("faq_mappings.json"),
    }
}

class ZhidaoQa():
    def __init__(self, config_option="prod", dryrun=True):
        self.esdata = collections.defaultdict(list)
        self.dryrun = dryrun
        self.datasets = ES_DATASET_CONFIG
        self.esconfig = es_api.get_esconfig(config_option)
        self.api_nlp = ZhidaoNlp()
        if not self.dryrun:
            es_api.batch_init(self.esconfig, self.datasets.values())

    def merge_chat(self, option="question"):
        filenames = []
        for dataset_index in ["chat8cmu6w","chat8xianer12w"]:
            filenames.extend( self._filter_filenames(dataset_index, option))

        self._merge_chat(filenames, option)

    def test(self, dataset_index="chat8xianer12w", option="query"):
        filename_todo = getLocalFile("input/{}_todo.txt".format(option))
        print "filename_todo",  filename_todo
        q_todo = set()
        if os.path.exists(filename_todo):
            q_todo = libfile.file2set(filename_todo)
            gcounter["q_todo"] = len(q_todo)
            print "filename_todo",  filename_todo, len(q_todo)

        filename_skip = getLocalFile("input/{}_skip.txt".format(option))
        print "filename_skip",  filename_skip
        q_skip = set()
        if os.path.exists(filename_skip):
            q_skip = libfile.file2set(filename_skip)
            gcounter["q_skip"] = len(q_skip)
            print "filename_skip",  filename_skip, len(q_skip)

        data = {}
        q_all = set()
        dirname = getLocalFile( "output0623/{}*worker*json.txt".format(dataset_index) )

        for filename in glob.glob(dirname):
            print filename
            gcounter["files"]+=1

            for line in libfile.file2list(filename):
                entry = json.loads(line)
                query = entry["query"]

                #print entry.keys()
                if "items_all" not in entry:
                    gcounter["selected_no_data"]+=1
                    continue
                elif len(entry["items_all"])==0:
                    gcounter["selected_no_item"]+=1
                    continue


                if q_skip and query in q_skip:
                    gcounter["items_skip"]+=1
                    q_all.add(query)
                    continue

                if self.api_nlp.detect_skip_words(query):
                    gcounter["selected_query_skipwords"]+=1
                    q_all.add(query)
                    continue

                items_select = self.api_nlp.select_qapair_0624(query, entry["items_all"])
                if items_select:
                    gcounter["selected_yes"]+=1
                    q_all.add(query)
                else:
                    gcounter["selected_no"]+=1

                for item in items_select:
                    item["id"]= es_api.gen_es_id(item["question"]+item["answers"])
                    if item["id"] in data:
                        continue

                    label = self.filter_qa_by_label("", item["question"], item["answers"])
                    if label:
                        item["label"] = label
                    else:
                        item["label"] = u""
                    xlabel = re.sub(":.*$","",item["label"])
                    gcounter["data_with_label_{}".format( xlabel )]+=1
                    gcounter["items"]+=1

                    data[item["id"]] = item
                #ret = libfile.readExcel(["category","question","answers"], filename, start_row=1)

        if q_todo:
            q_todo.difference_update(q_all)
            filename_output = getLocalFile("edit0623/query_miss_{}.xls".format(option))
            libfile.lines2file(sorted(list(q_todo)), filename_output)
            gcounter["q_all"] = len(q_all)
            gcounter["q_miss"] = len(q_todo)

    def _merge_chat(self, filenames, option):
        filename_todo = getLocalFile("input/{}_todo.txt".format(option))
        print "filename_todo",  filename_todo
        q_todo = set()
        if os.path.exists(filename_todo):
            q_todo = libfile.file2set(filename_todo)
            gcounter["q_todo"] = len(q_todo)
            print "filename_todo",  filename_todo, len(q_todo)

        filename_skip = getLocalFile("input/{}_skip.txt".format(option))
        print "filename_skip",  filename_skip
        q_skip = set()
        if os.path.exists(filename_skip):
            q_skip = libfile.file2set(filename_skip)
            gcounter["q_skip"] = len(q_skip)
            print "filename_skip",  filename_skip, len(q_skip)

        data = {}
        q_all = set()
        for filename in filenames:
            #print filename
            gcounter["files"]+=1
            ret = libfile.readExcel(["category","question","answers"], filename, start_row=1)
            if ret:
                for items in ret.values():
                    for item in items:
                        gcounter["items"]+=1

                        q_all.add(item["question"])

                        if q_skip and item["question"] in q_skip:
                            gcounter["items_skip"]+=1
                            continue

                        item["id"]= es_api.gen_es_id(item["question"]+item["answers"])
                        if item["id"] in data:
                            continue

                        for dataset_index in ["chat8cmu6w","chat8xianer12w"]:
                            if dataset_index  in filename:
                                gcounter["from_"+dataset_index] += 1

                        label = self.filter_qa_by_label(item["category"], item["question"], item["answers"])
                        if label:
                            item["label"] = label
                            #print "SKIP", label, "\t---\t", item["question"], "\t---\t", item["answers"]
                            #gcounter["_esdata_label_{}".format(label)]+=1
                        #elif not self.api_nlp.is_question_baike(item["question"]):
                        #    item["label"] = u"百科"
                        else:
                            item["label"] = u""
                        xlabel = re.sub(":.*$","",item["label"])
                        gcounter["data_with_label_{}".format( xlabel )]+=1

                        data[item["id"]] = item
                        item_new = {}
                        for p in ["question","answers","id"]:
                            item_new[p] = item[p]

        gcounter["data"] = len(data)
        results = sorted(data.values(),  key=lambda x:x["question"])
        print len(data), len(results)
        filename_output = getLocalFile("output/edit_{}.xls".format(option))
        libfile.writeExcel(results, ["label","question", "answers"], filename_output)

        filename_output = getLocalFile("edit0623/sample1000_edit_{}.xls".format(option))
        libfile.writeExcel(libdata.items2sample(data.values(), limit=1000), ["label","question", "answers"], filename_output)

        if q_todo:
            q_todo.difference_update(q_all)
            filename_output = getLocalFile("edit0623/question_miss_{}.xls".format(option))
            libfile.lines2file(sorted(list(q_todo)), filename_output)
            gcounter["q_all"] = len(q_all)
            gcounter["q_miss"] = len(q_todo)

        page_size = 2000
        max_page = len(results)/page_size + 1
        for i in range(max_page):
            filename_output = getLocalFile("edit0623/edit_{}_{}.xls".format( option, i))
            #print filename_output
            idx_start = i*page_size
            idx_end = min(len(results),(i+1)*page_size)
            libfile.writeExcel(results[idx_start:idx_end], ["label","question", "answers"], filename_output)

    def index_chat(self, dataset_index = "chat8cmu6w", option="question"):
        filenames = self._filter_filenames(dataset_index, option)
        self._index_qa(filenames, dataset_index)



    def _filter_filenames(self,  dataset_index, option):
        gcounter[dataset_index] = 1
        gcounter[option] = 1
        dirname = getLocalFile( "output0623/{}*worker*xls".format(dataset_index) )
        print dirname
        filenames = []

        if option == "query":
            for filename in glob.glob(dirname):
                if not "query" in filename:
                    continue
                filenames.append(filename)
        else:
            for filename in glob.glob(dirname):
                if "query" in filename:
                    continue
                filenames.append(filename)
        return filenames

    def filter_qa_by_label(self, cat, q, a, filter_option=0):
        if filter_option == 1:
            #有标记都不用
            if len(cat) > 0:
                return cat
            else:
                #无标记的过滤敏感词
                return ""
        else:
            #有标记的保持
            if len(cat) > 0:
                #keep human label
                return cat
            else:
                #无标记的过滤敏感词
                #re-evaluate label
                label = self.api_nlp.get_chat_label(q, a)
                return label


    def _index_qa(self, filenames, dataset_index, filter_option=0):
        ids = set()

        for filename in filenames:
            print filename

            gcounter["files"]+=1
            ret = libfile.readExcel(["category","question","answers"], filename, start_row=1)
            if ret:
                for items in ret.values():
                    for item in items:
                        gcounter["items"]+=1

                        item["id"]= es_api.gen_es_id(item["question"])
                        if item["id"] in ids:
                            continue

                        label = self.filter_qa_by_label("{}".format(item["category"]), item["question"], item["answers"], filter_option=filter_option)
                        if label:
                            print "SKIP", label, "\t---\t", item["question"], "\t---\t", item["answers"]
                            gcounter["esdata_label_{}".format(label)]+=1
                            if filter_option in [1]:
                                continue

                        ids.add(item["id"])
                        item_new = {}
                        for p in ["question","answers","id"]:
                            item_new[p] = item[p]
                        self.upload(dataset_index, item_new)
        self.upload(dataset_index)
        gcounter["esdata"] = len(ids)

    def index_edit_xianer7w_rewrite(self):
        dataset_index = "xianer7w_rewrite"
        gcounter[dataset_index] = 1

        ids = set()

        filename = getLocalFile( "label0625/xianer7w_rewrite_map.xlsx" )
        print filename

        gcounter["files"]+=1
        ret = libfile.readExcel(["question","old_answers", "answers"], filename, start_row=0)

        #collect answer mapping
        map_answers = {}
        for item in ret.values()[0]:
            if item.get("old_answers"):
                a_old = item["old_answers"].strip()
            if item.get("answers"):
                a = item["answers"].strip()

            if a and a_old:
                map_answers[a_old] = a

        print len(map_answers)



        filename = getLocalFile( "label0625/xianer7w_rewrite.xlsx" )
        print filename

        gcounter["files"]+=1
        ret = libfile.readExcel(["question","old_answers", "answers"], filename, start_row=0)

        #use mapping
        for item in ret.values()[0]:
            gcounter["items"]+=1
            q = item["question"]
            if item["old_answers"]:
                a = map_answers.get(item["old_answers"])
            else:
                a = ""

            if not a:
                #print "SKIP no mapping", q, item["old_answers"]
                gcounter["items_no_mapping"]+=1
                continue

            qa = q + a
            item["id"]= es_api.gen_es_id(q)
            if item["id"] in ids:
                gcounter["items_skip_dup"]+=1
                continue

            skip_words = self.api_nlp.detect_skip_words(qa, check_list=["skip_words_all","skip_words_zhidao"])
            if skip_words:
                print "SKIP", u"/".join(skip_words), "\t---\t", item["question"], "\t---\t", a
                gcounter["items_skip_minganci"]+=1
                continue

            ids.add(item["id"])
            item_new = {
                "question": q,
                "answers": a,
                "id": item["id"] ,
            }
            self.upload(dataset_index, item_new)
        self.upload(dataset_index)
        gcounter["esdata"] = len(ids)



    def index_edit(self, option="question"):
        dataset_index = "zhidao_{}".format(option)
        gcounter[option] = 1
        dirname = getLocalFile( "label0627/*{}*xls*".format(option) )
        print dirname
        filenames = glob.glob(dirname)

        ids = set()

        for filename in filenames:
            print filename

            gcounter["files"]+=1
            ret = libfile.readExcel(["category","question","answers", "type"], filename, start_row=1)
            if ret:
                for items in ret.values():
                    for item in items:
                        gcounter["items"]+=1

                        qa = u"{}{}".format(item["question"],item["answers"])
                        item["id"]= es_api.gen_es_id(qa)
                        if item["id"] in ids:
                            gcounter["items_skip_dup"]+=1
                            continue

                        if not item["type"] in [1,"1"]:
                            gcounter["items_skip_drop"]+=1
                            continue

                        skip_words = self.api_nlp.detect_skip_words(qa, check_list=["skip_words_all","skip_words_zhidao"])
                        if skip_words:
                            print "SKIP", u"/".join(skip_words), "\t---\t", item["question"], "\t---\t", item["answers"]
                            gcounter["items_skip_minganci"]+=1
                            continue

                        ids.add(item["id"])
                        item_new = {}
                        for p in ["question","answers","id"]:
                            item_new[p] = item[p]
                        self.upload(dataset_index, item_new)
        self.upload(dataset_index)
        gcounter["esdata"] = len(ids)

    def index_qa_simple(self, dataset_index):
        dirname = getLocalFile( "{}/*.xls*".format(dataset_index) )
        print dirname
        filenames = []

        for filename in glob.glob(dirname):
            filenames.append(filename)
        self._index_qa(filenames, dataset_index, filter_option=1)



    def index_xianer12w_test(self):
        dataset_index = "xianer12w_test"
        filename = getLocalFile("input/chat8xianer12w.txt")
        visited = set()
        for line in libfile.file2list(filename):

            if line in visited:
                continue

            visited.add(line)
            gcounter["lines"]+=1
            item = {
                "question": line,
                "answers": u"无语",
                "id": es_api.gen_es_id(line)
            }

            self.upload(dataset_index, item)
        self.upload(dataset_index)

    def upload(self, dataset_index, item=None):
        bucket = self.esdata[dataset_index]
        if item:
            bucket.append(item)

        if item is None or len(bucket) == 5000:
            if not self.dryrun:
                es_api.run_esbulk_rows(bucket, "index", self.esconfig, self.datasets[dataset_index] )
            else:
                print "dryrun, upload ", len(bucket)
            gcounter["uploaded_esdata_{}".format(dataset_index)] +=  len(bucket)
            self.esdata[dataset_index] = []


















    def init_from_json(self):
        map_items = {}
        dirname = getLocalFile( "raw/chat0708/*" )
        for filename in glob.glob(dirname):
            src = os.path.basename(filename).replace(".txt","")
            for line in libfile.file2list(filename):
                gcounter["total_"+src] +=1
                item = json.loads(line)
                item["source"] = src

                item["answers"] = clean_answer(item["answers"])
                item["question"] = clean_question(item["question"])
                if len(item["answers"]) <2:
                    gcounter["items_skip_empty_answer"]+=1
                    continue

                label = ""
                if not label:
                    label = self.api_nlp.detect_skip_words(item["answers"])
                    if label:
                        label = u"敏感词：{}".format( u",".join(label))
                        print label, item["answers"]
                        gcounter["minganci_answer"]+= 1
                    else:
                        label = ""
                if not label:
                    if re.search("^[0-9\-]$",item["answers"]):
                        label = "number"
                item["label"] = label

                q = item["question"]
                if q not in map_items:
                    map_items[q] = item
                    gcounter["from_"+src] +=1
                else:
                    map_items[q] = item
                    gcounter["overwrite_"+src] +=1
                    print "overwrite", q, src, map_items[q]["answers"], item["answers"]



        gcounter["init_from_json"] = len(map_items)

        filename = getLocalFile("temp/qa0708chat.xls")
        items = sorted(map_items.values(), key= lambda x:x["question"])
        libfile.writeExcel(items, ["label", "question", "answers", "source"], filename)



    def init_xianer7w_rewrite(self):
        dataset_index = "xianer7w_rewrite"
        gcounter[dataset_index] = 1

        ids = set()

        filename = getLocalFile( "raw/rewrite/xianer7w_rewrite_map.xlsx" )
        print filename

        gcounter["files"]+=1
        ret = libfile.readExcel(["question","old_answers", "answers"], filename, start_row=0)

        #collect answer mapping
        map_answers = {}
        for item in ret.values()[0]:
            if item.get("old_answers"):
                a_old = item["old_answers"].strip()
            if item.get("answers"):
                a = item["answers"].strip()

            if a and a_old:
                map_answers[a_old] = a

        print len(map_answers)



        filename = getLocalFile( "raw/rewrite/xianer7w_rewrite.xlsx" )
        print filename

        gcounter["files"]+=1
        ret = libfile.readExcel(["question","old_answers", "answers"], filename, start_row=0)

        #use mapping
        items = []
        for item in ret.values()[0]:
            gcounter["items"]+=1
            q = item["question"]
            if item["old_answers"]:
                a = map_answers.get(item["old_answers"])
            else:
                a = ""

            if not a:
                #print "SKIP no mapping", q, item["old_answers"]
                gcounter["items_no_mapping"]+=1
                continue

            qa = q + a
            item["id"]= es_api.gen_es_id(q)
            if item["id"] in ids:
                gcounter["items_skip_dup"]+=1
                continue

            skip_words = self.api_nlp.detect_skip_words(qa, check_list=["skip_words_all"])
            if skip_words:
                print "SKIP", u"/".join(skip_words), "\t---\t", item["question"], "\t---\t", a
                gcounter["items_skip_minganci"]+=1
                continue

            ids.add(item["id"])
            item_new = {
                "question": q,
                "answers": a,
                "id": item["id"] ,
            }
            items.append(item_new)

        gcounter["qa0708rewrite"] = len(ids)

        filename = getLocalFile("temp/qa0708rewrite.xls")
        libfile.writeExcel(items, ["label", "question", "answers"], filename)


    def init_zhidao_qa(self):
        #clean rewrite

        dataset_index_list = [
            "qa0708query",
            "qa0708question",
        ]
        for dataset_index in dataset_index_list:
            dirname = getLocalFile("raw/{}/*".format(dataset_index))
            map_items = {}
            for filename in glob.glob(dirname):

                gcounter["files"]+=1
                ret = libfile.readExcel(["category","question","answers", "type"], filename, start_row=1)
                if ret:
                    for items in ret.values():
                        for item in items:
                            gcounter["items"]+=1

                            qa = u"{}{}".format(item["question"],item["answers"])
                            item["id"]= es_api.gen_es_id(qa)
                            if item["id"] in map_items:
                                gcounter["items_skip_dup"]+=1
                                continue

                            if not item["type"] in [1,"1"]:
                                gcounter["items_skip_drop"]+=1
                                continue

                            item["answers"] = clean_answer(u"{}".format(item["answers"]))
                            item["question"] = clean_question(u"{}".format(item["question"]))
                            if len(item["answers"]) <2:
                                gcounter["items_skip_empty_answer"]+=1
                                continue

                            skip_words = self.api_nlp.detect_skip_words(item["answers"], check_list=["skip_words_all","skip_words_zhidao"])
                            if skip_words:
                                print "SKIP", u"/".join(skip_words), "\t---\t", item["question"], "\t---\t", item["answers"]
                                gcounter["items_skip_minganci"]+=1
                                continue

                            item_new = {"source": dataset_index}
                            for p in ["question","answers","id"]:
                                item_new[p] = item[p]
                            map_items[item_new["question"]] = item_new

            gcounter["init_from_{}".format(dataset_index)] = len(map_items)
            print len(map_items)

            filename = getLocalFile("temp/{}.xls".format(dataset_index))
            items = sorted(map_items.values(), key= lambda x:x["question"])
            libfile.writeExcel(items, ["label", "question", "answers", "source"], filename)

def clean_question(text):
    temp = text+" "
    temp = clean_emoji(temp)
    temp = re.sub(ur"@[\S]+\s+","", temp).strip()
    temp = re.sub(ur"[～~，。？！,：\.!\?\-\s]+$","", temp)
    return temp

def clean_dupword(text):
    if not text:
        return ""

    temp = u""
    w_prev = ""
    for w in text:
        if w in "." or w not in w_prev :
            temp += w
            w_prev = w
        else:
            if len(w_prev)<=1:
                temp += w
            w_prev += w
    if temp != text:
        print "dupword", text, temp
    return temp

def clean_answer(text):
    if not text:
        return ""
    temp = text
    temp = clean_emoji(temp)
    temp = re.sub(ur"\[[^\]]+\]","", temp)
    temp = re.sub(ur"[╮\(╯_╰\)╭…～（）［］【】～~]+","", temp)
    temp = re.sub(ur"[~，。？！,：\.!\?\-\s]+$","", temp)
    if re.search(ur"[^\u4E00-\u9FA5，。？！,\d\w\.!\?\-\s]", temp):
        temp = ""
    temp = clean_dupword(temp)
    return temp

def clean_emoji(text):
    text = text.encode("utf-8").decode("utf-8","ignore")

    emoji_pattern_text = "[{}{}{}{}{}]".format(
        u"\U0001F600-\U0001F64F",  # emoticons
        u"\U0001F300-\U0001F5FF",  # symbols & pictographs
        u"\U0001F680-\U0001F6FF",  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF",  # flags (iOS)
        u'\u2600-\u26FF\u2700-\u27BF',
        )
    #print emoji_pattern_text
    emoji_pattern = re.compile(emoji_pattern_text, flags=re.UNICODE)

    return emoji_pattern.sub(r'', text)
    #print(emoji_pattern.sub(r'', text)) # no emoji

def main():
    #print sys.argv

    if len(sys.argv)<2:
        print "unsupported"
        return

    config = {}

    option= sys.argv[1]

    if "test" == option:
        agt = ZhidaoQa(config_option=config_option, dryrun=False)
        #agt.test(option="query")

    elif "init_rewrite" == option:
        """
            python chat/task_es.py clean_prod

        """
        agt = ZhidaoQa(config_option="local", dryrun=True)
        agt.init_xianer7w_rewrite()


    elif "init_from_json" == option:
        """
            python chat/task_es.py clean_prod

        """
        agt = ZhidaoQa(config_option="local", dryrun=True)
        agt.init_from_json()


    elif "init_zhidao_qa" == option:
        """
            python chat/task_es.py clean_prod

        """
        agt = ZhidaoQa(config_option="local", dryrun=True)
        agt.init_zhidao_qa()







    elif "clean_prod" == option:
        """
            python chat/task_es.py clean_prod

        """
        agt = ZhidaoQa(config_option="local", dryrun=True)
        agt.clean_prod()


    elif "index_chat" == option:
        """
            python chat/task_es.py index_chat chat8xianer12w
            python chat/task_es.py index_chat chat8cmu6w
            python chat/task_es.py index_xianer12w_test
        """
        dataset_index = "chat8cmu6w"
        if len(sys.argv)>3:
            dataset_index = sys.argv[3]
        dryrun = False
        if len(sys.argv)>3:
            dryrun = True
        agt = ZhidaoQa(config_option="prod", dryrun=dryrun)
        agt.index_chat(dataset_index)


    elif "merge_chat" == option:
        """
            python chat/task_es.py merge_chat question
            python chat/task_es.py merge_chat query
        """
        if len(sys.argv)>2:
            option = sys.argv[2]
            agt = ZhidaoQa()
            agt.merge_chat(option)
    elif "index_chat_debug" == option:
        dataset_index = "chat8cmu6w"
        if len(sys.argv)>2:
            dataset_index = sys.argv[2]
        agt = ZhidaoQa(config_option="local", dryrun=False)
        agt.index_chat(dataset_index)








    elif "index_edit_xianer7w_rewrite" == option:
        """
            python chat/task_es.py index_edit_xianer7w_rewrite prod
        """
        if len(sys.argv)>2:
            config_option = sys.argv[2]
            agt = ZhidaoQa(config_option=config_option, dryrun=False)
            agt.index_edit_xianer7w_rewrite()

    elif "index_simple" == option:
        """
            python chat/task_es.py index_simple baike_qa local
            python chat/task_es.py index_simple qa0708chat10k local
        """
        if len(sys.argv)>3:
            dataset_index = sys.argv[2]
            config_option = sys.argv[3]
            agt = ZhidaoQa(config_option=config_option, dryrun=False)
            agt.index_qa_simple(dataset_index)




    elif "index_xianer12w_test" == option:
        """
            python chat/task_es.py index_xianer12w_test  prod
        """
        if len(sys.argv)>2:
            config_option = sys.argv[2]
            agt = ZhidaoQa(config_option=config_option, dryrun=False)
            agt.index_xianer12w_test()



    else:
        print "unsupported"

if __name__ == '__main__':
    main()
    print json.dumps(gcounter, ensure_ascii=False, indent=4, sort_keys=True)
