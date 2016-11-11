#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# http://www.sfda.gov.cn/WS01/CL0885/165486.html 附件
# http://www.sfda.gov.cn/WS01/CL0884/165474.html 文本
# http://www.sfda.gov.cn/WS01/CL0369/165149.html 多表 
# http://www.sfda.gov.cn/WS01/CL0369/45877.html 多个冒号
from datetime import datetime

import json
import urllib
import re
import urlparse
import lxml.html
import time
import requests
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper
from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER


def get_formatted_table(table_node):
    tr_labels = table_node.xpath('.//tr')
    result_list = []
    keys = []
    for td_label in tr_labels[0].xpath('.//td'):
            word = ''.join(td_label.xpath('.//text()'))
            keys.append(re.sub(u'[\s]', u'',word))
    values = []
    for tr_label in tr_labels[1:]:
        for td_label in table_node.xpath('.//tr[2]//td'):
            word = ''.join(td_label.xpath('.//text()'))
            if word.strip():
                values.append(word.strip())
        item = dict(zip(keys, values))
        result_list.append(item)
    return result_list

def parse_page(url):
    content = process._downloader.downloader_wrapper(
                url,
                'yaojianjugmpgsp',
                1,
                timeout = 10,
                refresh = True)
    if not content:
        raise IOError('This page might be 404')
    dom = lxml.html.fromstring(content)
    title = dom.xpath('//td[@class="articletitle3"]//text()')[0]
    published_time = dom.xpath('//td[@class="articletddate3"]//text()')[0]
    content_block = dom.xpath('//td[@class="articlecontent3"]')[0]
    print title.encode('utf-8')
    record = {
        'title'             : title,
        'published_time'    : published_time,
        'source'            : url,
        'table_list'        : [],
        'article_content'   : '',
    }

    table_node = content_block.xpath('.//table')
    if table_node:                                  # 为格式化的图表
        table_node = table_node[0]
        record['table_list'] = get_formatted_table(table_node)
        parent = 0
        while table_node != content_block:
            siblines = table_node.xpath('./preceding-sibling::*')
            if siblines:
                for i in siblines:
                    record['article_content'] += ''.join(i.xpath('.//text()')).strip()
                break
            table_node = table_node.xpath('./..')[0]
    else:                                          # 可能为文字的图表
        record['table_list'].append({})
        texts = content_block.xpath('.//text()')
        for line in texts:
            line = line.strip()
            if not line:
                continue
            if re.search(u'[:：]', line):
                key = re.split(u'[:：]', line)[0]   
                value = ':'.join(re.split(u'[:：]', line)[1:])
                if not value:
                    continue
                record['table_list'][0][key] = value
            else:
                record['article_content'] += line

    if not record['table_list'][0]:                  # 两种方式都没得到table
        raise IOError('There is no table element in this url')
    for table in record['table_list']:
        table['access_time'] = datetime.datetime.utcnow().isoformat()
    return process._cache.post(url, json.dumps(record, ensure_ascii=False), refresh=True)


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    print (url)
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))

    if not hasattr(process,'_regs'):
        setattr(process, '_regs', {
            'homepage': re.compile('http://www.sfda.gov.cn/WS01/(.*?)/$'),
            'detail'  : re.compile('http://www.sfda.gov.cn/WS01/(.*?)/(.*?).html')
        })
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        print label
        if label == 'homepage':
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                refresh = True)
            dom = lxml.html.fromstring(content)
            total_content = dom.xpath('//td[@class="pageTdSTR15"]//text()')[0]
            total_page    = int(re.findall(u'共(\d+)页', total_content)[0])
    
            for page in range(2, total_page):
                print (page)
                hrefs = dom.xpath('//td[@class="ListColumnClass15"]/a/@href')
                urls = []
                for href in hrefs:
                    href = re.sub(u'\.\.', u'', href)       # 网址是以..开头的相对路径
                    href = 'http://www.sfda.gov.cn/WS01' + href
                    urls.append(href)
                    manager.put_urls_enqueue(batch_id, urls)
                page_url = '{}index_{}.html'.format(url, page)
                content = process._downloader.downloader_wrapper(
                    page_url,
                    batch_id,
                    gap,
                    timeout = timeout,
                    refresh = True)
                dom = lxml.html.fromstring(content)
            return True
        elif label == 'detail':
            return parse_page(url)
