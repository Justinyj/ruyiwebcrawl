#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import sys
import collections
import codecs
import datetime
import json
import re
import time

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import libfile
import libdata
from api_zhidao import ZhidaoNlp
from api_zhidao import ZhidaoFetch
from api_classify import TextClassifier


def show_help():
    print "unsupported";

def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "learn_baike" == option:
        api = TextClassifier()
        api.train()



if __name__ == "__main__":
    main()
