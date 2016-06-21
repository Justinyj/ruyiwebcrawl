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
import es

from hzlib import libfile
from hzlib.api_zhidao import ZhidaoFetch



def main():
    #print sys.argv

    if len(sys.argv)<2:
        return

    config = {}

    agt = ZhidaoFetch(config)
    option= sys.argv[1]
    if "realtime_chat" == option:
        query = u"你喜欢蓝色吗？"
        if len(sys.argv)>2:
            query = sys.argv[2]
        query_filter = 2
        best_item = agt.search_chat_best(query)
        print json.dumps(best_item, ensure_ascii=False, indent=4, sort_keys=True)


    else:
        print "unsupported"

if __name__ == '__main__':
    main()
