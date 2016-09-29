#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# 爬取逻辑：
# 1.先通过首字母得到各个药材的MBID，如刀豆的MBID是133
# 2.再通过http://www.zyctd.com/Breeds/GetMCodexPoolListByMBID这个URL得到每个MBID下的各种规格-产地，和相应的MBSID
# 如post刀豆的MBID=133后返回一个列表：红统-较广 MBSID=133301、白统-较广 MBDIS=13302
# 3.最后通过这个MBSID，再对一个URL进行query，可以获得价格历史，价格历史中会分不同市场

import json
import urllib
import re
import urlparse
import lxml.html
import time
import requests
from datetime import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info('process {}'.format(url))
    if not hasattr(process, '_downloader'):
        headers = {}
        setattr(process, '_downloader', DownloadWrapper(None, headers))

    if not hasattr(process,'_regs'):
        setattr(process, '_regs', {
            'first_letter': re.compile('^[A-Z]$'),
            'drug': re.compile('(\d+)')
        })

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        if label == 'first_letter':
            first_letter = url
            data = {
                'Data':'{{\"url\": \"\", \"letter\": \"{}\"}}'.format(first_letter)  # form data示例： Data:{"letter":"J","url":""} 
            }      

            query_url = 'http://yaocai.zyctd.com/Ajax/AjaxHandle.ashx?CommandName=common/MCodexService/GetCodexNameByLetter'
            content = process._downloader.downloader_wrapper(query_url,
                batch_id,
                gap,
                method='post',
                data=data,
                timeout=timeout,
                refresh=True)
            if not content:
                return False

            drug_list = json.loads(content)
            MBID_list = [ str(drug[u'MBID'])for drug in drug_list[u'Data']]
            manager.put_urls_enqueue(batch_id, MBID_list) # 每个MBID为一个数字

        elif label == 'drug':
            mbid = url
            query_url = 'http://www.zyctd.com/Breeds/GetMCodexPoolListByMBID' 
            data = {
                    'mbid':'{}'.format(mbid),
                    'IsMarket':'true'
            }
            content = process._downloader.downloader_wrapper(query_url,
                batch_id,
                gap,
                method='post',
                data=data,
                timeout=timeout,
                refresh=True)
            if not content:
                return False

            item = json.loads(content)
            sub_drug_list = item[u'Data']
            if not sub_drug_list:           # 请求成功然而列表为空，说明这种药材没有价格数据，属正常情况
                return True

            for sub_drug in sub_drug_list:    # eg：一个刀豆list里根据不同规格和产地的刀豆会分为不同的sub_drug,拥有不同的MBSID
                price_history_url = 'http://www.zyctd.com/Breeds/GetPriceTrend'
                data = {
                    'MBSID'   : sub_drug['MBSID'],
                    'IsMarket': 'true'
                }
                price_content = process._downloader.downloader_wrapper(price_history_url,
                    batch_id,
                    gap,
                    method='post',
                    data=data,
                    timeout=timeout,
                    refresh=True)
                if not price_content:
                    return False

                spec_info = sub_drug['MSpec'].split(' ')        
                productGrade = spec_info[0]                                         
                if len(spec_info)==2:                           
                    productPlaceOfOrigin = spec_info[1]         # MSpec一般情况示例： 大统 东北  OR 统 较广
                else:                                           # MSpec特殊情况示例： 统
                    productPlaceOfOrigin = ''
                price_item = json.loads(price_content)[u'Data']
                price_data = price_item[u'PriceChartData']      # 注意price_data是一个字符串，需要再次loads后变为一个列表，每个列表代表一个药市，其中还嵌套着价格列表,价格里时间表示为时间戳等。
                                                                # 由于后续处理较复杂，决定将这部分留到清洗脚本中完成，爬虫层面避免过多的清洗操作。

                if price_data == '[]':                          # 即使存在这种规格，也有可能会没有价格历史
                    return True
                result_item ={
                    'name' : sub_drug['MName'],
                    'productGrade': productGrade,
                    'productPlaceOfOrigin':productPlaceOfOrigin,
                    'source'        : 'http://www.zyctd.com/jiage/xq{}.html'.format(mbid),
                    'access_time'   : datetime.utcnow().isoformat(),
                    'price_data'    : price_data
                }

                if not process._cache.post(url, json.dumps(result_item, ensure_ascii = False), refresh = True):
                    return False
            return True