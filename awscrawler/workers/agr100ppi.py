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
from downloader.caches3 import CacheS3
from lxml import etree
from downloader.cache import Cache
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://agr.100ppi.com/price/'
# SERVER = 'http://192.168.1.179:8000'
def process(url, batch_id, parameter, manager, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))
    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CacheS3(head + '-json-' + tail))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'prd': re.compile(r'http://agr.100ppi.com/price/plist-(\d+)(-{1,3})(\d+).html')
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = float(gap)
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    print(url)
    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        refresh=True
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

        if label == 'prd':
            prd_name = page.xpath('/html/body/div[1]/div[2]/a[3]/span/text()')[0]
            data = {}
            dics = ''
            for i in range(2,50): # i 为 table 的行数，第一行为header，不同商品表中行数可能不同，但均小于50，设置循环上限为50在获取不到信息时break
                data[u'商品名称'] = prd_name
                data[u'报价机构'] = page.xpath("//table/tr[{}]/td[1]/div/a/text()".format(str(i)))[0].strip() if  page.xpath("//table/tr[{}]/td[1]/div/a/text()".format(str(i))) else ''
                data[u'报价类型'] = page.xpath("//table/tr[{}]/td[2]/text()".format(str(i)))[0].strip() if page.xpath("//table/tr[{}]/td[2]/text()".format(str(i))) else ''
                data[u'报价'] = page.xpath("//table/tr[{}]/td[3]/text()".format(str(i)))[0].strip() if page.xpath("//table/tr[{}]/td[3]/text()".format(str(i))) else ''
                data[u'规格'] = page.xpath("//table/tr[{}]/td[4]/text()".format(str(i)))[0].strip() if page.xpath("//table/tr[{}]/td[4]/text()".format(str(i))) else ''
                data[u'产地'] = page.xpath("//table/tr[{}]/td[5]/div/text()".format(str(i)))[0].strip() if page.xpath("//table/tr[{}]/td[5]/div/text()".format(str(i))) else ''
                data[u'发布时间'] = page.xpath("//table/tr[{}]/td[6]/text()".format(str(i)))[0].strip() if page.xpath("//table/tr[{}]/td[6]/text()".format(str(i))) else ''
                
                if not data[u'报价机构']:
                    break
                dics += json.dumps(data, encoding='utf-8', ensure_ascii=False) + '\n'
            urls = page.xpath('//div[@class=\"page-inc magt10\"]/a[11]/@href')
            if not urls:
                urls = page.xpath('//div[@class=\"page-inc magt10\"]/a[10]/@href')
            # print(dics)
            # print(urls)
            get_logger(batch_id, today_str, '/opt/service/log/').info(urls[0] + ' added to queue')
            if not dics:
                return True
            urls = [ urlparse.urljoin(SITE, url) for url in urls ]
            manager.put_urls_enqueue(batch_id, urls)
            return process._cache.post(url, dics)


