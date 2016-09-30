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
from datetime import datetime, timedelta
from lxml import etree
from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://chem.100ppi.com/price/'
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
            'main': re.compile(r'http://chem.100ppi.com/price/plist-(\d+)(-{1,3})(\d+).html'),
            'prd': re.compile(r'http://www.100ppi.com/price/detail-(\d+).html')
        })

    def safe_state(statement):
        return statement[0] if statement else ''
    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
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
    
    # content.encoding='gb18030'
    # if kwargs and kwargs.get("debug"):
    # get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        page = etree.HTML(content)

        if label == 'main':
            # print("adding chem prds")
            prd_links = page.xpath('//table/tr/td[1]/div/a/@href')
            newest = page.xpath("//table/tr[2]/td[6]/text()")[0]
            if newest.replace(u'-','') not in [today_str, yesterday_str]:
                return True 
            if not prd_links:
                # print('end of pages')
                get_logger(batch_id, today_str, '/opt/service/log/').info('end of pages')
                return True

            next_pat = re.compile(r'plist-(\d+)(-{1,3})(\d+).html')
            current = next_pat.search(url)
            current = str(int(current.group(3)) + 1)
            next_page = url[:url.rfind('-') + 1] + current + '.html'

            prd_links.append(urlparse.urljoin(SITE, next_page))
            get_logger(batch_id, today_str, '/opt/service/log/').info('||'.join(prd_links) + ' added to queue')
            manager.put_urls_enqueue(batch_id, prd_links)
            return True

        else:
            data = {}
            data['name'] = page.xpath("/html/body/div[8]/div[1]/span[2]/text()")[0]
            # print(data['name'], 'prd page')
            data['source'] = url
            # data['prd_header'] = page.xpath("//div[@class=\"mb20\"]/table/tr/th/text()")
            # data['prd_infos'] = page.xpath("//div[@class=\"mb20\"]/table/tr/td/text()")
            prd_header = page.xpath("/html/body/div[8]/div[2]/div[1]/div[1]/h3/text()")[0]
            idx_left, idx_right = prd_header.find(u'('), prd_header.find(u')')
            data[u'报价类型'] = prd_header[idx_left+1: idx_right]
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

            # print(json.dumps(data, encoding='utf-8', ensure_ascii=False))
            if data[u'发布时间'].replace(u'-','') not in [today_str, yesterday_str]:
                return True 
            dics = json.dumps(data, encoding='utf-8', ensure_ascii=False)
            get_logger(batch_id, today_str, '/opt/service/log/').info(dics + ' saved to S3')
            return process._cache.post(url, dics)




