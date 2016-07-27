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
sys.path.append('..')
from downloader.caches3 import CacheS3
from lxml import etree
from downloader.cache import Cache
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME

reload(sys)
sys.setdefaultencoding('utf-8')
# SITE = 'http://kw.fudan.edu.cn'
SITE = 'http://china.chemnet.com/'
SERVER = 'http://192.168.1.179:8000'
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
            'main': re.compile(urlparse.urljoin(SITE,"company/supplier\.cgi\?f=;t=company;terms=%B9%AB%CB%BE;search=company;property=;regional=;submit.x=25;submit.y=16;submit=%BB%AF%B9%A4%CB%D1%CB%F7;p=\d+")),
            'company': re.compile(r"http://(.+?).cn.chemnet.com/show/"),
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    today_str = datetime.now().strftime('%Y%m%d')

    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')

    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        timeout=timeout,
        encoding='utf-8'
        )
    # print (content)
    if content == '':
        return False
    
    # for n,l in zip(nodes,link):
    #     print(n.strip())
    #     print(l.strip())
    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue

        # entity = urllib.unquote(m.group(1))
        if label == 'main':
            print("add company")
            page = etree.HTML(content)
            # nodes = page.xpath("//*[@id=\"main\"]/div[1]/div/div[2]/dl/dt/a/text()")
            links = page.xpath("//*[@id=\"main\"]/div[1]/div/div[2]/dl/dt/a/@href")
            manager.put_urls_enqueue(batch_id, links)

            return True
        else:
            data = json.dumps({'url':url,'body': content})
            print("Post to Cache")

            # if kwargs and kwargs.get("debug"):
            #     get_logger(batch_id, today_str, '/opt/service/log/').info('start post {} json'.format(label))

            return process._cache.post(url, data)



# process(SITE,'testfw-20160725',"get:1:false:10:",'',debug=True)
