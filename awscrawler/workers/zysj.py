#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# 数据存储格式：{ '摘录'：'中华药典', '药品名称':'当归'...}   
#               { '摘录'：'中华本草', '药品名称':'当归'...}     ...

from __future__ import print_function, division
import sys
import json
import urllib
import re
import urlparse
from datetime import datetime
from lxml import etree
from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://www.zysj.com.cn'
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
            'main': re.compile(r'http://www.zysj.com.cn/zhongyaocai/index__\d+.html'),
            'prd': re.compile(r'http://www.zysj.com.cn/zhongyaocai/yaocai_\w/(.+?).html')
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout
        )
    # print(content)
    if content == '':
        # print("no content")
        get_logger(batch_id, today_str, '/opt/service/log/').info(url + ' no content')
        return False
    
    # content.encoding='gb18030'
    # if kwargs and kwargs.get("debug"):
    # get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        page = etree.HTML(content)
        if label == 'main':
            get_logger(batch_id, today_str, '/opt/service/log/').info("adding Chinese Meds")
            meds = page.xpath("//*[@id=\"list\"]/ul/li/a/@href")  # links for meds in main page
            meds = [ urlparse.urljoin(SITE, med) for med in meds ]
            # print(meds[:5])
            get_logger(batch_id, today_str, '/opt/service/log/').info('adding Meds urls into queue')
            manager.put_urls_enqueue(batch_id, meds)
            return True

        elif label == 'prd':
            med_name = page.xpath("//*[@id=\"article\"]/h1/text()")[0]
            get_logger(batch_id, today_str, '/opt/service/log/').info(med_name + " main page")
            # print(med_name,"main page")
            dics = ''
            books = content.split('<hr />')     # 用来分开不同的药典
            if len(books) == 2:                 # 只有一个药典的情况
                books = [ books[0] ]
            else:                               # 有多个药典的情况
                books = books[1:-1]
            for book in books:
                page = etree.HTML(book.replace('<strong>', '').replace('</strong>', '').replace('<sub>', '').replace('</sub>', ''))

                med_info = page.xpath("//p/text()")
                data = {}
                data['ss'] = url

                for info in med_info:
                    m = re.compile(r'【.+?】').match(info.encode('utf-8'))
                    if m:
                        prop = m.group(0)[3:-3]
                        cleaned = re.sub(r'【.+?】', '', info.encode('utf-8'))
                        data[prop] = cleaned
                    else:
                        data[prop] += '\n' + info.encode('utf-8')
                dics += json.dumps(data) + '\n'    # 一行是一个药典json，不同药典间用换行符分开

            get_logger(batch_id, today_str, '/opt/service/log/').info('start posting prd page to cache')
            return process._cache.post(url, dics)


