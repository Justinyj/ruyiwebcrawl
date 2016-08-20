#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
import re
import urlparse
import lxml.html
from datetime import datetime

from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    home_page = 'http://app1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=23&tableName=TABLE23&title=GMP%C8%CF%D6%A4&bcId=118715589530474392063703010776'
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_reg'):
        setattr(process, '_reg', {
            'detail': re.compile('http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=23&tableName=TABLE23&tableView=GMP%C8%CF%D6%A4&Id=(\d+)'),
        })

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    today_str = datetime.now().strftime('%Y%m%d')

    if kwargs and kwargs.get("debug"):
        get_logger(batch_id, today_str, '/opt/service/log/').info('start download')


    data = {
        'tableId ':' 23',
        'State ':' 1',
        'bcId ':' 118715589530474392063703010776',
        'State ':' 1',
        'tableName ':' TABLE23',
        'State ':' 1',
        'viewtitleName ':' COLUMN152',
        'State ':' 1',
        'viewsubTitleName ':' COLUMN151',
        'State ':' 1',
        'curstart ':' 2',
        'State ':' 1',
        'tableView ':' GMP%E8%AE%A4%E8%AF%81',
        'State ':' 1'
    }

    if url == home_page:
        if kwargs and kwargs.get("debug"):
            get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')
        page = 1
        while 1 :
            data['curstart'] = page
            content = process._downloader.downloader_wrapper(home_page,
                batch_id,
                0,
                method = 'post',
                timeout = timeout,
                refresh = True,
                data = data
            )
            import requests
            print (len(requests.post(url, data=data).text))
            print (content)
            # if page == 3:
            #     return
            ids = re.findall(u'国产药品&Id=(\d+)', content)
            if not ids:
                break
            url_pattern = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=23&tableName=TABLE23&tableView=GMP%C8%CF%D6%A4&Id={}'
            urls = []
            for drug_id in ids:
                url = url_pattern.format(drug_id)
                urls.append(url)
            manager.put_urls_enqueue(batch_id, urls)
            page += 1
            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('going to page{}'.format(page))
            
        return

    elif process._reg['detail'].match(url):

        content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            timeout=timeout,
            )
        if content == '':
            return False
        if kwargs and kwargs.get("debug"):
            get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')
        dom = lxml.html.fromstring(content)
        table = dom.xpath('//tr')

        item = {
            'province ' :             table[1].xpath('./td')[1].xpath('./text()'),
            'certification_number ' : table[2].xpath('./td')[1].xpath('./text()'),
            'certification_version ' : table[11].xpath('./td')[1].xpath('./text()'),
            'scope_of_certification' : table[5].xpath('./td')[1].xpath('./text()'),
            'begin_date' : table[6].xpath('./td')[1].xpath('./text()'),
            'end_date ' : table[8].xpath('./td')[1].xpath('./text()'),
        }
        for  k,v in item.iteritems():
            if len(v) > 0:
                item[k] = v[0]
            else :
                item[k] = None

        return process._cache.post(url, json.dumps(item, ensure_ascii = False))



