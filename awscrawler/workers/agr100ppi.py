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
            'main': re.compile(r'http://agr.100ppi.com/price/plist-(\d+)(-{1,3})(\d+).html'),
            'prd': re.compile(r'http://www.100ppi.com/price/detail-(\d+).html')
        })

    def safe_state(statement):
        return statement[0] if statement else ''
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
        print("no content")
        # get_logger(batch_id, today_str, '/opt/service/log/').info(url + ' no content')
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
            print("adding agricultural prds")
            prd_links = page.xpath('//table/tr/td[1]/div/a/@href')

            next_page = page.xpath('//div[@class=\"page-inc magt10\"]/a[11]/@href')
            if not next_page:
                next_page = page.xpath('//div[@class=\"page-inc magt10\"]/a[10]/@href')
            if not next_page:
                return True
            prd_links.append(urlparse.urljoin(SITE, next_page[0]))
            print(prd_links)
            # get_logger(batch_id, today_str, '/opt/service/log/').info(urls[0] + ' added to queue')
            manager.put_urls_enqueue(batch_id, prd_links)
            return True

        else:

            data['name'] = page.xpath("/html/body/div[8]/div[1]/span[2]/text()")[0]
            print(data['name'], 'prd page')
            # data['prd_header'] = page.xpath("//div[@class=\"mb20\"]/table/tr/th/text()")
            # data['prd_infos'] = page.xpath("//div[@class=\"mb20\"]/table/tr/td/text()")
            data[u'报价机构'] = page.xpath("/html/body/div[8]/div[2]/div[2]/div[2]/table/tr[1]/td/h3/text()")[0].strip()
            data[u'商品报价'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[1]/td[1]/text()"))
            data[u'发布时间'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[1]/td[2]/text()"))
            data[u'出产地'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[2]/td[1]/text()"))
            data[u'有效期'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[2]/td[2]/text()"))
            data[u'仓储地'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[3]/td[1]/text()"))
            data[u'包装说明'] = safe_state(page.xpath("//div[@class=\"mb20\"]/table/tr[3]/td[2]/text()"))
            data[u'生产厂家'] = safe_state(page.xpath("/html/body/div[8]/div[2]/div[1]/div[2]/div/div[2]/text()"))

            info = {}
            table_header = page.xpath("//table[@class=\"mb20 st2-table tac\"]/tr/th/text()")
            table_content = page.xpath("//table[@class=\"mb20 st2-table tac\"]/tr/td/text()")
            for header, cont in zip(table_header, table_content):
                info[header] = cont
            data[u'详细信息'] = info

            contact = {}
            contact[u'联系人'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[2]/td[2]/text()"))
            contact[u'电话'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[3]/td[2]/text()"))
            contact[u'传真'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[4]/td[2]/text()"))
            contact[u'邮件'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[5]/td[2]/text()"))
            contact[u'手机'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[6]/td[2]/text()"))
            contact[u'地址'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[7]/td[2]/text()"))
            contact[u'网址'] = safe_state(page.xpath("//div[@class=\"connect\"]/table/tr[8]/td[2]/text()"))
            data[u'联系方式'] = contact

            print(json.dumps(data, encoding='utf-8', ensure_ascii=False))
            return process._cache.post(url, data)




