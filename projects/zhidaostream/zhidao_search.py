#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import requests
import urllib

from zhidao_downloader import zhidao_downloader

def zhidao_search(word, timeout=10):
    word = urllib.quote(word.encode('utf-8')) if isinstance(word, unicode) else urllib.quote(word)
    query_url = 'http://zhidao.baidu.com/index/?word={}'.format(word)

    resp = requests.get(query_url, headers=HEADERS, timeout=timeout)
    # resp.headers: 'content-type': 'text/html;charset=UTF-8',
    # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
    if resp.status_code == 200:
        return zhidao_search_parse(resp.content)


def zhidao_search_parse(content):
    """
    :param content: content is uft-8 html string, aka response.content in zhidao_search
    """
    return re.findall('href="(?:http://zhidao.baidu.com)?/question/(\d+).html', content)


