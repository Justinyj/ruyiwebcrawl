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
import json
import random
import glob
import collections

from es import es_api
from hzlib import libfile
from hzlib import libdata

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

gcounter = collections.Counter()

ES_DATASET_CONFIG ={
    "chat8cmu6w":
    {   "description":"知道短问答",
        "es_index":"ruyiwebcrawl_zhidaoqa_0623",
        "es_type":"default",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "chat8xianer12w":
    {   "description":"知道短问答 chat8xianer12w",
        "es_index":"ruyiwebcrawl_zhidaoqa_0623",
        "es_type":"chat8xianer12w",
        "filepath_mapping": getTheFile("faq_mappings.json"),
    },
    "xianer12w":
        {   "description":"贤二短问答",
            "es_index":"ruyiwebcrawl_zhidaoqa_0623",
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
        if not self.dryrun:
            es_api.batch_init(self.esconfig, self.datasets.values())

    def index_chat(self, dataset_index = "chat8cmu6w"):
        dirname = getLocalFile( "output0623/{}*worker*xls".format(dataset_index) )
        print dirname

        for filename in glob.glob(dirname):
            print filename
            gcounter["files"]+=1
            ret = libfile.readExcel(["category","question","answers"], filename, start_row=1)
            if ret:
                for items in ret.values():
                    for item in items:
                        if item["category"]:
                            continue
                        gcounter["items"]+=1

                        item["id"]= es_api.gen_es_id(item["question"]+item["answers"])
                        item_new = {}
                        for p in ["question","answers","id"]:
                            item_new[p] = item[p]
                        self.upload(dataset_index, item_new)
        self.upload(dataset_index)

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
        dataset_index = "chat8cmu6w"
        if len(sys.argv)>2:
            dataset_index = sys.argv[2]
        agt = ZhidaoQa(config_option="prod", dryrun=False)
        agt.index_chat(dataset_index)
    elif "index_chat_debug" == option:
        dataset_index = "chat8cmu6w"
        if len(sys.argv)>2:
            dataset_index = sys.argv[2]
        agt = ZhidaoQa(config_option="local", dryrun=False)
        agt.index_chat(dataset_index)
    elif "index_xianer12w" == option:
        agt = ZhidaoQa(config_option="prod", dryrun=False)
        agt.index_xianer12w()
    else:
        print "unsupported"

if __name__ == '__main__':
    main()
    print json.dumps(gcounter, ensure_ascii=False, indent=4, sort_keys=True)
