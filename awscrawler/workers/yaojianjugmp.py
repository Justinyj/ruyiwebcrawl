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
    home_page = 'http://qy1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=23&tableName=TABLE23&title=GMP%C8%CF%D6%A4&bcId=118715589530474392063703010776'
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_reg'):
        setattr(process, '_reg', {
            'detail': re.compile('http://qy1.sfda.gov.cn/datasearch/face3/content.jsp\?tableId=23&tableName=TABLE23&tableView=GMP%C8%CF%D6%A4&Id=(\d+)'),
        })

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    today_str = datetime.now().strftime('%Y%m%d')


    data = {
        'tableId':'23',
        'State':'1',
        'bcId':'118715589530474392063703010776',
        'State':'1',
        'curstart':'4',
        'State':'1',
        'tableName':'TABLE23',
        'State':'1',
        'viewtitleName':'COLUMN152',
        'State':'1',
        'viewsubTitleName':'COLUMN151',
        'State':'1',
        'tableView':'GMP%E8%AE%A4%E8%AF%81',
        'State':'1',
    }
    if url == home_page:
        page = 1
        while 1 :
            data['curstart'] = page
            content = process._downloader.downloader_wrapper('http://qy1.sfda.gov.cn/datasearch/face3/search.jsp',
                batch_id,
                gap,
                method = 'post',
                timeout = timeout,
                refresh = True,
                data = data
            )
            ids = re.findall(u'GMP认证&Id=(\d+)', content)
            if not ids:
                break
            url_pattern = 'http://qy1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=23&tableName=TABLE23&tableView=GMP%C8%CF%D6%A4&Id={}'
            urls = []
            for drug_id in ids:
                url = url_pattern.format(drug_id)
                urls.append(url)
            manager.put_urls_enqueue(batch_id, urls)
            page += 1
        return True
    elif process._reg['detail'].match(url):
        content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            timeout=timeout,
            )
        if content == '':
            return False
        dom = lxml.html.fromstring(content)
        table = dom.xpath('//tr')

        item = {
            'source':url,
            'access_time': datetime.utcnow().isoformat()
        }
        tr_labels = dom.xpath('//tr')
        for tr_label in tr_labels[1:]:
            key     = ''.join(tr_label.xpath('.//td[1]//text()')).strip()
            value   = ''.join(tr_label.xpath('.//td[2]//text()')).strip()
            if value and key != u'注':
                item[key] = value
        return process._cache.post(url, json.dumps(item, ensure_ascii = False))
