#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import requests
import urllib

from .zhidao_downloader import zhidao_download

def zhidao_search(word, batch_id, gap=3, timeout=10):
    word = urllib.quote(word.encode('utf-8')) if isinstance(word, unicode) else urllib.quote(word)
    query_url = 'http://zhidao.baidu.com/index/?word={}'.format(word)

    ret = zhidao_download(query_url, batch_id, gap, timeout=timeout, encode='utf-8', error_check=False)
    # resp.headers: 'content-type': 'text/html;charset=UTF-8',
    # resp.content: <meta content="application/xhtml+xml; charset=utf-8" http-equiv="content-type"/>
    if ret is False:
        return False
    return zhidao_search_parse(ret)


def zhidao_search_parse(content):
    """
    :param content: content is uft-8 html string, aka response.content in zhidao_search
    """
    return re.findall('href=\"(?:http://zhidao.baidu.com)?/question/(\d+).html', content)

