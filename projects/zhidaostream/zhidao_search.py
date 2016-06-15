#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import requests
import urllib
import lxml.html.soupparser as soupparser

from zhidao_downloader import zhidao_downloader


def zhidao_search(word, timeout=10):
    word = urllib.quote(word.encode('utf-8')) if isinstance(word,
                                                            unicode) else urllib.quote(word)
    query_url = 'http://zhidao.baidu.com/index/?word={}'.format(word)

    resp = requests.get(query_url, headers=HEADERS, timeout=timeout)
    # resp.headers: 'content-type': 'text/html;charset=UTF-8',
    # resp.content: <meta content="application/xhtml+xml; charset=utf-8"
    # http-equiv="content-type"/>
    if resp.status_code == 200:
        return zhidao_search_parse(resp.content)


def zhidao_search_parse(content):
    """
    :param content: content is uft-8 html string, aka response.content in zhidao_search
    """
    dom = soupparser.fromstring(content)

    recommend = dom.xpath('//div[@id="wgt-autoask"]')
    HasRecommend = 0
    if recommend:
        # once recommend get picked,the url must exists
        url = recommend[0].xpath('.//a/@href')[0]
        q_id = re.findall('zhidao.baidu.com/question/(\d+).html', url)
        if q_id:
            HasRecommend = 1
            value_text = recommend[0].xpath('.//i[@class="i-agree"]/../text()')
            value_text = value_text[1]
            recommend_value = int(re.findall('(\d+)', value_text)[0])
            recommend_id = q_id[0]
        else:
            pass

    normal = dom.xpath('//dl[contains(@class,"dl")]') #last class will be "dl dl-last"
    legal_node_list = []
    legal_id_list = []
    for node in normal:
        url = node.xpath('./dt/a/@href')[0]
        q_id = re.findall('zhidao.baidu.com/question/(\d+).html', url)
        if q_id:
            legal_node_list.append(node)
            legal_id_list.append(q_id[0])

    if HasRecommend:
        max_val = recommend_value
    else:
        max_val = -1
    max_id = None
    for index in range(len(legal_node_list)):
        node = legal_node_list[index]
        node_val_text = node.xpath('.//i[@class="i-agree"]/../text()')
        if node_val_text:  # eg:['\n', '41\n']
            node_val = int(node_val_text[1].strip())
            if  node_val>max_val:
                max_val = node_val
                max_id = legal_id_list[index]

    result = []
    if HasRecommend:
        result.append(recommend_id)
    if max_id:
        result.append(max_id)
    if not result:
        result.append(legal_id_list[0])