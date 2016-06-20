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

reload(sys)
sys.setdefaultencoding("utf-8")
import downloader

from downloader.cache import Cache
from downloader.downloader_wrapper import DownloadWrapper
from hzlib import libfile

#############
# config
VERSION ='v20160620'

CONFIG_T = {
     "batch_ids": {
         "index": "dongcaigonggao-index0620-{}".format(VERSION),
         "page": "dongcaigonggao-page-{}".format(VERSION),
     },
     "cache_server": "http://52.196.166.54:8000",
     "crawler": {
         "gap": 3,
         "timeout": 10,
         "encoding": "gb18030",
         "error_check": True
     }
}

CONFIG = {
    "prod": {},
    "local": {},
}
CONFIG["prod"].update(CONFIG_T)
CONFIG["local"].update(CONFIG_T)
CONFIG["local"]["cache_server"] = "http://192.168.1.179:8000"
#     "cache_server": "http://52.192.116.149:8000",


def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getWorkFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+VERSION+"/"+filename

def gen_url():
    urls = []
    for i in range(1,35268):
        url = "http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}".format(i)
        urls.append(url)
    filename = getWorkFile("urls_gonggao_index.raw.txt")
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    libfile.lines2file(urls, filename)

def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    option= sys.argv[1]
    if "gen_url" == option:
        gen_url()

    else:
        print "unsupported"

if __name__ == '__main__':
    main()
