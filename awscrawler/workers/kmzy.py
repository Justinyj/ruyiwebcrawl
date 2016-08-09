#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# json format:
# {"data": [["2016-01", 11.0], ["2016-02", 11.0], ["2016-03", 11.0], ["2016-04", 10.0], ["2016-05", 9.5], ["2016-06", 9.5], 
#  ["2016-07", 9.4]], "specs": "统/河南", "name": "白花蛇舌草"}
# {"data": [["2016-01", 11.0], ["2016-02", 11.0], ["2016-03", 11.0], ["2016-04", 10.0], ["2016-05", 9.5], ["2016-06", 9.5], 
#  ["2016-07", 9.4]], "specs": "统/甘肃", "name": "白花蛇舌草"}

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
import time
from crawlerlog.cachelog import get_logger
from settings import REGION_NAME

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://www.kmzyw.com.cn/'
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
            'main': re.compile(r'http://www.kmzyw.com.cn/bzjsp/biz_price_search/price_index_search.jsp'),
            'prd': re.compile(r'http://www.kmzyw.com.cn/bzjsp/Biz_price_history/price_history_search.jsp\?name=(.*?)')
        })

    def timestamp2datetime(timestamp):
        if isinstance(timestamp, (int, long, float)):
            dt = datetime.utcfromtimestamp(timestamp)
        else:
            return "Not a valid timestamp"
        mid = '-0' if dt.month < 10 else '-'
        return str(dt.year) + mid + str(dt.month) 

    post_form = {
                'pagecode': None,
                'search_site': '%25E4%25BA%25B3%25E5%25B7%259E',

    }

    method, gap, js, timeout, data = parameter.split(':')
    gap = float(gap)
    timeout = int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')
    
    get_logger(batch_id, today_str, '/opt/service/log/').info('start parsing url')
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        
        if label == 'main':
            total_page = 10 # 初始化为一个较小的数，之后在获取页面内容后会更新此总页数
            page_num = 1
            while page_num < total_page + 1:

                post_form['pagecode'] = page_num 
                # print(page_num)
                content = process._downloader.downloader_wrapper(url,
                batch_id,
                gap,
                method='post',
                data=post_form,
                timeout=timeout,
                refresh=True
                )
                # print(content)
                data = json.loads(content)
                total_page = data['page']   # 从json中读出总页数
                drugs = []
                drug_url = 'http://www.kmzyw.com.cn/bzjsp/Biz_price_history/price_history_search.jsp?name={}'
                for row in data['rows']:
                    # print(row['drug_name'])
                    drugs.append(drug_url.format(urllib.quote(str(row['drug_name'])).replace('%', '%25')))
                manager.put_urls_enqueue(batch_id, drugs)
                page_num += 1
            
            return True

        elif label == 'prd':

            content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            timeout=timeout,
            refresh=True
            )
            page = etree.HTML(content)
            prd = page.xpath("/html/body/section[2]/h1/text()")[0]
            idx = prd.index(u'品种')
            prd = prd[:idx]
            get_logger(batch_id, today_str, '/opt/service/log/').info(prd + " main page")
            price_hist  = page.xpath("/html/head/script[12]/text()")[0]
            # print(price_hist)
            data_pat = re.compile(r'series : \[(.*),marker')
            m = data_pat.findall(price_hist)
            dics = ''
            if m:
                # print(m[0])
                data = m[0].split(',marker : { enabled : false ,radius : 3 } ,tooltip : { valueDecimals : 2 }},')
                for d in data:
                    name = 'name'
                    data = 'data'
                    dic = eval(d + '}')
                    # print(dic)
                    cleaned = {}
                    cleaned['specs'] = dic['name']
                    cleaned['name'] = prd
                    cleaned['data'] = [ (timestamp2datetime(int(price[0]) // 1000), price[1]) for price in dic['data'] ]
                    dics += json.dumps(cleaned, encoding='utf-8') + '\n'

                
            else:
                get_logger(batch_id, today_str, '/opt/service/log/').info('not match')
            
            get_logger(batch_id, today_str, '/opt/service/log/').info('start posting prd page to cache')
            return process._cache.post(url, dics)


