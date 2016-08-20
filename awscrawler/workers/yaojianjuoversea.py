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
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')

from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info(url)
    home_page = 'http://app1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=36&tableName=TABLE36&title=%BD%F8%BF%DA%D2%A9%C6%B7&bcId=124356651564146415214424405468'
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_reg'):
        setattr(process, '_reg', {
            'detail': re.compile('http://app1.sfda.gov.cn/datasearch/face3/content.jsp\?tableId=36&tableName=TABLE36&Id=(\d+)'),
        })

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    
    #if kwargs and kwargs.get("debug"):
    get_logger(batch_id, today_str, '/opt/service/log/').info('start download')


    data = {
        'tableId' : '36',
        'State' : '1',
        'bcId' : '124356651564146415214424405468',
        'State' : '1',
        'State' : '1',
        'tableName' : 'TABLE36',
        'State' : '1',
        'viewtitleName' : 'COLUMN361',
        'State' : '1',
        'viewsubTitleName' : 'COLUMN354,COLUMN355,COLUMN356,COLUMN823',
        'curstart':'2',
        'State' : '1',
        'State' : '1',
    }

    if url == home_page:
        #if kwargs and kwargs.get("debug"):
        page = 1
        while 1 :
            time.sleep(gap)
            get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url at page {}'.format(page))
            data['curstart'] = page
            content = process._downloader.downloader_wrapper('http://app1.sfda.gov.cn/datasearch/face3/search.jsp',
                batch_id,
                gap,
                method = 'post',
                timeout = timeout,
                refresh = True,
                data = data,
                encoding = 'utf-8'
            )
            #get_logger(batch_id, today_str, '/opt/service/log/').info(content)
            ids = re.findall(u'进口药品&Id=(\d+)', content)
            get_logger(batch_id, today_str, '/opt/service/log/').info(ids)
            if not ids:
                get_logger(batch_id, today_str, '/opt/service/log/').info('End at {} pages'.format(page))
                break
            # if page == 3:
            #     break
            get_logger(batch_id, today_str, '/opt/service/log/').info('ids : {}'.format(ids))
            url_pattern = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=36&tableName=TABLE36&Id={}'
            urls = []
            for drug_id in ids:
                url = url_pattern.format(drug_id)
                urls.append(url)

            manager.put_urls_enqueue(batch_id, urls)
            page += 1
            get_logger(batch_id, today_str, '/opt/service/log/').info('going to page{}'.format(page))
        return True

    elif process._reg['detail'].match(url):


        content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            timeout = timeout,
            refresh = True
            )
        if content == '':
            return False

        dom = lxml.html.fromstring(content)
        table = dom.xpath('//tr')
        item = {
            'license_number':                   table[1].xpath('./td')[1].xpath('./text()'),           # [u'注册证号']
            'old_license_number':               table[2].xpath('./td')[1].xpath('./text()'),           # [u'原注册证号']
            'packaging_license_number':         table[4].xpath('./td')[1].xpath('./text()'),           # [u'分包装批准文号']
            'company_chs':                      table[5].xpath('./td')[1].xpath('./text()'),           # [u'公司名称（中文）']
            'company_eng':                      table[6].xpath('./td')[1].xpath('./text()'),           # [u'公司名称（英文）']
            'product_name_chs':                 table[11].xpath('./td')[1].xpath('./text()'),          # [u'产品名称（中文）']
            'product_name_eng':                 table[12].xpath('./td')[1].xpath('./text()'),          # [u'产品名称（英文）']
            'commodity_name_chs':               table[13].xpath('./td')[1].xpath('./text()'),          # [u'商品名（中文）']
            'commodity_name_eng':               table[14].xpath('./td')[1].xpath('./text()'),          # [u'商品名（英文）']
            'drug_form':                        table[15].xpath('./td')[1].xpath('./text()'),          # [u'剂型（中文）']
            'specification':                    table[16].xpath('./td')[1].xpath('./text()'),          # [u'规格（中文）']
            'dosage':                           table[17].xpath('./td')[1].xpath('./text()'),          # [u'包装规格（中文）']
            'manufacturer_chs':                 table[18].xpath('./td')[1].xpath('./text()'),          # [u'生产厂商（中文）']
            'manufacturer_eng':                 table[19].xpath('./td')[1].xpath('./text()'),          # [u'生产厂商（英文）']
            'manuf_address_chs':                table[20].xpath('./td')[1].xpath('./text()'),          # [u'厂商地址（中文）']
            'manuf_address_eng':                table[21].xpath('./td')[1].xpath('./text()'),          # [u'厂商地址（英文）']
            'manuf_country_chs':                table[22].xpath('./td')[1].xpath('./text()'),          # [u'厂商国家/地区（中文）']
            'manuf_country_eng':                table[23].xpath('./td')[1].xpath('./text()'),          # [u'厂商国家/地区（英文）']
            'packaging_company_name':           table[26].xpath('./td')[1].xpath('./text()'),          # [u'分包装企业名称']
            'packaging_company_address':        table[27].xpath('./td')[1].xpath('./text()'),          # [u'分包装企业地址']
            'category':                         table[31].xpath('./td')[1].xpath('./text()'),          # [u'产品类别']
            'standard_code':                    table[32].xpath('./td')[1].xpath('./text()'),          # [u'药品本位码']
            'source' :                             [url], #设为list格式与之前字段统一，在下面的循环里一并取出
        }

        for k,v in item.iteritems():
            if len(v) > 0:
                item[k] = v[0]
            else :
                item[k] = None


        return process._cache.post(url, json.dumps(item, ensure_ascii = False))



