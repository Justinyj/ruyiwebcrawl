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
        "es_index":"ruyiwebcrawl_zhidaoqa_0624",
        "es_type":"default",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "chat8xianer12w":
    {   "description":"知道短问答 chat8xianer12w",
        "es_index":"ruyiwebcrawl_zhidaoqa_0624",
        "es_type":"chat8xianer12w",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "xianer12w":
        {   "description":"贤二短问答",
            "es_index":"ruyiwebcrawl_zhidaoqa_0624",
            "es_type":"xianer12w",
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
        self._index_chat(filenames, dataset_index)

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

    def filter_qa_by_label(self, cat, q, a):
        if len(cat) == 1:
            #keep human label
            return cat
        else:
            #re-evaluate label
            label = self.api_nlp.get_chat_label(q, a)
            return label

    def _index_chat(self, filenames, dataset_index):
        ids = set()

        for filename in filenames:
            print filename

            gcounter["files"]+=1
            ret = libfile.readExcel(["category","question","answers"], filename, start_row=1)
            if ret:
                for items in ret.values():
                    for item in items:
                        gcounter["items"]+=1

                        item["id"]= es_api.gen_es_id(item["question"]+item["answers"])
                        if item["id"] in ids:
                            continue

                        label = self.filter_qa_by_label(item["category"], item["question"], item["answers"])
                        if label:
                            print "SKIP", label, "\t---\t", item["question"], "\t---\t", item["answers"]
                            gcounter["esdata_label_{}".format(label)]+=1

                        ids.add(item["id"])
                        item_new = {}
                        for p in ["question","answers","id"]:
                            item_new[p] = item[p]
                        self.upload(dataset_index, item_new)
        self.upload(dataset_index)
        gcounter["esdata"] = len(ids)

    def index_xianer12w(self):
        dataset_index = "xianer12w"
        filename = getLocalFile("input/chat8xianer12w.txt")
        for line in libfile.file2list(filename):

            gcounter["lines"]+=1
            item = {
                "question": line,
                "answers": u"呵呵",
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




def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    config = {}

    option= sys.argv[1]

    if "index_chat" == option:
        """
            python chat/task_es.py index_chat chat8xianer12w
            python chat/task_es.py index_chat chat8cmu6w
            python chat/task_es.py index_xianer12w
        """
        dataset_index = "chat8cmu6w"
        if len(sys.argv)>2:
            dataset_index = sys.argv[2]
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
    elif "index_xianer12w" == option:
        agt = ZhidaoQa(config_option="prod", dryrun=False)
        agt.index_xianer12w()
    elif "test" == option:
        agt = ZhidaoQa(config_option="prod", dryrun=False)
        agt.test(option="query")
    else:
        print "unsupported"

if __name__ == '__main__':
    main()
    print json.dumps(gcounter, ensure_ascii=False, indent=4, sort_keys=True)
