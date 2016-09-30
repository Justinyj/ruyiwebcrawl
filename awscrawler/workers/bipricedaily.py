#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>


from __future__ import print_function, division
import sys
import json
import urllib
import re
import urlparse
# sys.path.append('..')
from datetime import datetime
from lxml import etree
from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://www.sge.com.cn'
# SERVER = 'http://192.168.1.179:8000'
def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'main': re.compile(r'http://jiage.cngold.org/jinshubi/list_3640_(\d+).html'),
            'info': re.compile(r'http://jiage.cngold.org/c/(\d+-\d+-\d+)/c(\d+).html'),
            'index': re.compile(r'http://jiage.cngold.org/jinshubi/index.html')
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    if url == 'http://jiage.cngold.org/jinshubi/list_3640_1.html':
        url = 'http://jiage.cngold.org/jinshubi/index.html'
    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout
        )
    # print(content)
    if content == '':
        get_logger(batch_id, today_str, '/opt/service/log/').info(url + ' no content')
        return False
    


    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            # print("not match")
            continue
        page = etree.HTML(content)

        if label == 'index':
            prices = page.xpath(".//ul[@class='list_baojia']/li/a/@href")
            # get_logger(batch_id, today_str, '/opt/service/log/').info(str(prices))
            manager.put_urls_enqueue(batch_id, prices[:3])
            
            return True

        elif label == 'info':
            dic = {}
            datestr = m.group(1)
            table = page.xpath(".//table//td/text()")
            table = [t.strip() for t in table]
            dic[u'产品名称'] = table[0]
            dic[u'产品价格'] = table[1]
            dic[u'价格单位'] = table[2]
            dic[u'涨跌'] = table[3]
            dic[u'日期'] = datestr
            dic[u'source'] = url
            dic[u'access_time'] = datetime.utcnow().isoformat()
            data = json.dumps(dic, ensure_ascii=False)
            # get_logger(batch_id, today_str, '/opt/service/log/').info(data)
            return process._cache.post(url, data)




