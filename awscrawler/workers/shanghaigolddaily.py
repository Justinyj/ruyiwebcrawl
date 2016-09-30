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
            'main': re.compile(r'http://www.sge.com.cn/xqzx/mrxq/index_(\d+).shtml'),
            'info': re.compile(r'http://www.sge.com.cn/xqzx/mrxq/(\d+).shtml'),
            'index': re.compile(r'http://www.sge.com.cn/xqzx/mrxq/index.shtml')
        })

    if url == 'http://www.sge.com.cn/xqzx/mrxq/index_2.shtml':
        url = 'http://www.sge.com.cn/xqzx/mrxq/index.shtml'

    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    # print(url)
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
            get_logger(batch_id, today_str, '/opt/service/log/').info('in list page')
            urls = page.xpath(".//ul[@id='zl_list']/li/a/@href")
            urls = [ urlparse.urljoin(SITE, list_url) for list_url in urls]
            get_logger(batch_id, today_str, '/opt/service/log/').info(str(urls))
            # get_logger(batch_id, today_str, '/opt/service/log/').info('||'.join(prd_links) + ' added to queue')
            manager.put_urls_enqueue(batch_id, urls[:3])
            
            return True

        elif label == 'info':
            dic = {}
            date = page.xpath(".//h5[@class='con_h5']/text()")[0].split(u'\xa0')[0]
            header = page.xpath(".//div[@id='page_con']/table/tbody/tr[1]/td//text()")
            infos = page.xpath(".//div[@id='page_con']/table/tbody/tr/td[1]//text()")
            infos = [ info.strip() for info in infos if info.strip() ]
            
            idx = -1
            for index, prod in enumerate(list(infos)):
                if prod.startswith('Pt99'):
                    idx = str(index + 1)
                    break
            if idx == -1:
                return True
            pt_infos = page.xpath(".//div[@id='page_con']/table/tbody/tr[{}]/td//text()".format(idx))

            if not pt_infos:
                get_logger(batch_id, today_str, '/opt/service/log/').info("No pt info on this page " + url)
                return True
            for col, value in zip(header, pt_infos):
                dic[col] = value.strip()
            dic[u'日期'] = date
            dic[u'source'] = url
            dic[u'access_time'] = datetime.utcnow().isoformat()
            data = json.dumps(dic, ensure_ascii=False)
            get_logger(batch_id, today_str, '/opt/service/log/').info(data)
            return process._cache.post(url, data)




