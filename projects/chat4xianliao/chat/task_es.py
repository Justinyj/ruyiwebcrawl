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
    "local":{ "qa":
        {   "description":"知道短问答",
            "es_index":"ruyiwebcrawl_zhidaoqa_0623",
            "es_type":"default",
            "filepath_mapping": getTheFile("faq_mappings.json"),
        },
    },
    "prod":{ "qa":
        {   "description":"知道短问答",
            "es_index":"ruyiwebcrawl_zhidaoqa_0623",
            "es_type":"default",
            "filepath_mapping": getTheFile("faq_mappings.json"),
        },
    }
}

class ZhidaoQa():
    def __init__(self, config_option="prod", dryrun=True):
        self.esdata = []
        self.dryrun = dryrun
        self.datasets = ES_DATASET_CONFIG[config_option]
        self.esconfig = es_api.get_esconfig(config_option)
        if not self.dryrun:
            es_api.batch_init(self.esconfig, self.datasets.values())

    def index(self):
        dirname = getLocalFile("output0623/*worker*xls")
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
                        self.upload(item_new, dataset_index="qa")
        self.upload(dataset_index="qa")

    def upload(self, item=None, dataset_index="qa"):
        if item:
            self.esdata.append(item)

        if item is None or len(self.esdata) == 1000:
            if not self.dryrun:
                es_api.run_esbulk_rows(self.esdata, "index", self.esconfig, self.datasets[dataset_index] )
            else:
                print "dryrun, upload ", len(self.esdata)
            gcounter["uploaded_esdata_{}".format(dataset_index)] +=  len(self.esdata)
            self.esdata = []




def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    config = {}

    option= sys.argv[1]

    if "index" == option:
        agt = ZhidaoQa(config_option="prod", dryrun=False)
        agt.index()
    elif "index_debug" == option:
        agt = ZhidaoQa(config_option="local", dryrun=False)
        agt.index()
    else:
        print "unsupported"

if __name__ == '__main__':
    main()
    print json.dumps(gcounter, ensure_ascii=False, indent=4, sort_keys=True)
