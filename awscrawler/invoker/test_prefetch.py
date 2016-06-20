import json
import sys
from  workers import prefetch
import os
import re

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def test_preftch(filename, prefetch_index):
    url = "http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=23"
    batch_id = "test_test_dongfangcaifu"

    with open(getTheFile("../"+filename)) as f:
        config = json.load(f)[prefetch_index]
        parameter = "{}:{}:{}:{}:{}".format(
        		config["crawl_http_method"],
        		config["crawl_gap"],
        		config["crawl_use_js_engine"],
        		config["crawl_timeout"],
                "data"
                )
        prefetch.process(url, batch_id, parameter, debug=True)

test_preftch("config_prefetch/config_dongfangcaifu.json", "prefetch_index")
