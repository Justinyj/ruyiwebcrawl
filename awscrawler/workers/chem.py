#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>


from __future__ import print_function, division
import sys
import json
import urllib
import re
import urlparse
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
SITE = 'http://china.chemnet.com'
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
            'main': re.compile(r'http://china.chemnet.com/hot-product/\w.html'),
            'prd': re.compile(r'http://china.chemnet.com/product/pclist--(.+?)--0.html'),
            'comps': re.compile(r'http://china.chemnet.com/product/search.cgi')
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    compspat = 'http://china.chemnet.com/product/search.cgi?skey={};use_cas=0;f=pclist;p={}'
    today_str = datetime.now().strftime('%Y%m%d')

    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        # encoding='gb18030',
        refresh=True
        )
    # print(content)
    if content == '':
        get_logger(batch_id, today_str, '/opt/service/log/').info(url + ' no content')
        return False
    

    # if kwargs and kwargs.get("debug"):
    get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        page = etree.HTML(content)
        if label == 'main':
            # print("add chems")
            chems = page.xpath("//*[@id=\"main\"]/div[1]/div[2]/dl/dd/ul/li/p[2]/a/@href")  # links for chems in main page
            chems = [ urlparse.urljoin(SITE, chem) for chem in chems]
            get_logger(batch_id, today_str, '/opt/service/log/').info('adding chems urls into queue')
            manager.put_urls_enqueue(batch_id, chems)
            return True

        elif label == 'prd':
            chem_uri = m.group(1)
            chem_name = page.xpath("//*[@id=\"main\"]/div[1]/div[1]/table/tr[1]/td[2]/text()")[0]
            get_logger(batch_id, today_str, '/opt/service/log/').info(chem_name + " main page")
            
            comps = page.xpath("//*[@id=\"main\"]/div[2]/div[2]/dl/dd/form/table/tr[1]/td[2]/a[1]")
            pagetext = page.xpath("//*[@id=\"main\"]/div[2]/div[2]/dl/dd/h6/div/text()[1]")
            # print(pagetext[0])
            total = int(re.compile(r'共有(\d+)条记录').search(pagetext[0].encode('utf-8')).group(1))
            total = total // 10 + 1 if total % 10 != 0 else total // 10
            data = json.dumps({'name':chem_name, 'url':url, 'body': content})
            new_urls = []
            for t in range(total):
                new_url = compspat.format(chem_uri, str(t))
                get_logger(batch_id, today_str, '/opt/service/log/').info("new url" + new_url)
                new_urls.append(new_url)
            manager.put_urls_enqueue(batch_id, new_urls)
            get_logger(batch_id, today_str, '/opt/service/log/').info('start posting prd page to cache')
            return process._cache.post(url, data)

        else:
            chem_name = page.xpath("//*[@id=\"main\"]/div[1]/div[1]/table/tr[1]/td[2]/text()")[0]
            comps = page.xpath("//*[@id=\"main\"]/div[2]/div[2]/dl/dd/form/table/tr[1]/td[2]/a[1]/text()")
            comps = [c for c in comps]
            data = json.dumps({'name':chem_name, 'companies':' '.join(comps)})
            get_logger(batch_id, today_str, '/opt/service/log/').info('start posting companies to cache')
            return process._cache.post(url, data)



# process('http://china.chemnet.com/product/search.cgi\?skey=%B1%BD%CD%AA;use_cas=0;f=pclist;p=1','testfw-20160725',"get:1:false:10:",'',debug=True)
