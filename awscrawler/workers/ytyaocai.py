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
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')

from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME

def process(url, batch_id, parameter, manager, *args, **kwargs):
    # 药材的详情页涉及2个部分：价格历史history和边栏sidebar，以下的ytw/second/是价格历史的url，返回一个大的json；
    # 所以在最后处理的时候还要额外向另一个url发送一次请求，以获得边栏信息,由于要储存到同一个result.json中，因此不再放入队列，而是直接在process里完成
    
    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info('process {}'.format(url))
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))

    if not hasattr(process,'_regs'):
        setattr(process, '_regs', {
            'home': re.compile('http://www.yt1998.com/variteyIndexInfo.html'),
            'kind': re.compile('http://www.yt1998.com/issueIndexInfo.html\?code='),
            'history':re.compile('http://www.yt1998.com/ytw/second/indexMgr/getIndexInfo.jsp\?code=(\d+)&type=1&varitey_name=(.*)') #这是价格历史的url
        })

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CacheS3(head + '-json-' + tail))

    if not hasattr(process,'_next_patterns'):
        setattr(process, '_next_patterns', {
            'home': 'http://www.yt1998.com/issueIndexInfo.html?code={}',                         #the format of kind
            'kind':'http://www.yt1998.com/ytw/second/indexMgr/getIndexInfo.jsp?code={}&type=1&varitey_name={}',  #the format of history
            'history':'http://www.yt1998.com/variteyIndexInfo.html?varitey_code={}'              #the format of sidebar
        })

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        get_logger(batch_id, today_str, '/opt/service/log/').info('label : {}'.format(label))
        if label in ['home', 'kind']:  #I handle home-page and kind-page in one code block cuz they are in same web format
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)

            dom = lxml.html.fromstring(content)
            dd_labels = dom.xpath('//dd')
            urls = []
            for single_dd in dd_labels:
                rels = single_dd.xpath('.//@rel')
                if not rels:
                    get_logger(batch_id, today_str, '/opt/service/log/').info('wrong rels content : {}'.format(rels))
                    continue
                for rel in rels:
                    code = rel.split(',')[-2]  #在home页面，rel的格式为 'Z,家种类' code为Z；在kind页面，rel格式为'Z,家种类,000001,枸杞'，code为000001
                    if label == 'home':
                        urls.append(process._next_patterns[label].format(code))
                    else: # label == 'kind'
                        name = str(rel.split(',')[-1])
                        urls.append(process._next_patterns[label].format(code, urllib.quote(name)))
            manager.put_urls_enqueue(batch_id, urls)


        elif label == 'history': #开始提取单种药品数据
            code = m.group(1)
            name = urllib.unquote(m.group(2))
            sidebar_url = process._next_patterns[label].format(code)
            sidebar_content = process._downloader.downloader_wrapper(
                sidebar_url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)

            sidebar_dom = lxml.html.fromstring(sidebar_content)
            sidebar_label = sidebar_dom.xpath('//div[@class="box-con-r fr"]/table//tr')
            if not isinstance(sidebar_label, list) or len(sidebar_label) != 19:
                get_logger(batch_id, today_str, '/opt/service/log/').info('not legal list!')
                return False

            sidebar_item = {} # 边栏信息
            for index in range(1, 16): 
                line_content = sidebar_label[index].xpath('./td/text()') #line content格式为 权重比：0.0278、市净率：2.00...  
                parts = line_content[0].split('：')      # chinese colon :left part as key,right part as value
                sidebar_item[parts[0]] = parts[1]

            line_content = sidebar_label[16].xpath('./th/text()')  #最后更新时间的样式与其他不同，为th
            parts = line_content[0].split('：') 
            sidebar_item[parts[0]] = parts[1]

            history_content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)

            if history_content == '':
                return False
            get_logger(batch_id, today_str, '/opt/service/log/').info('history downloading finished')
            
            history_item = json.loads(history_content)[u'DayMonthData']   #从结果中提取每天数据
            price_history = {} #价格历史
            for raw_daily_data in history_item:
                date = raw_daily_data[u'Date_time']
                price = raw_daily_data[u'DayCapilization']
                price_history[date] = price

            result_item = {}
            result_item['name'] = name
            result_item['info'] = sidebar_item
            result_item['price_history'] = price_history
            f = open('jiage.txt', 'a')
            f.write(json.dumps(result_item, ensure_ascii = False))
            f.close()
            return process._cache.post(url, json.dumps(result_item, ensure_ascii = False), refresh = True)
