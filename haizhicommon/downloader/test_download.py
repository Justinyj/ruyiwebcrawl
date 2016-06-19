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
from downloader import Downloader


def test_encoding_gb18030_20160619b():
    url = "http://zhidao.baidu.com/question/130330820.html"

    agt = Downloader("test", "http://127.0.0.1", request=True)
    content_unicode = agt.request_download(url)
    print content_unicode[:500]
    assert(type(content_unicode) == unicode)

def test_encoding_gb18030_20160619a():
    url = "http://zhidao.baidu.com/question/130330820.html"
    import requests
    import chardet
    r = requests.get(url)
    print r.encoding
    entry = chardet.detect(r.content[:500])
    print entry
    encoding_real = "gb18030"
    if entry:
        encoding_real = entry["encoding"]
    print r.content[:500].decode(encoding_real)

    try:
        r.content[:500].decode("utf-8")
        print "NO, should not reach here"
        assert(False)
    except:
        print "YES! the following code should raise exception !!!! "

def test_url2domain():
    agt = Downloader("test", "http://127.0.0.1", request=True)

    url = 'http://user:pass@example.com:8080'
    domain = agt.url2domain(url)
    assert(domain == "example.com")

    url = 'http://zhidao.baidu.com/search/?word=%22%E5%AE%87%E5%'
    domain = agt.url2domain(url)
    assert(domain == "zhidao.baidu.com")

def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "test" == option:
        pass

    elif "all" == option:
        test_url2domain()
        test_encoding_gb18030_20160619b()
        print "all done!"

    elif "encoding" == option:
        test_encoding_gb18030_20160619a()


if __name__ == "__main__":
    main()
